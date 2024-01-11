import modal
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from typing import Dict

from utils.helpers import fetch_domain_key, validate_dkim, sha256_hash
from utils.prove import run_prove_process
from utils.errors import Errors
from utils.env_utils import read_env_credentials
from utils.file_utils import write_file_to_local, read_proof_from_local
from utils.slack_utils import upload_file_to_slack

load_dotenv('./env')       # Load environment variables from .env file

# --------- VALIDATE EMAIL ------------

DOMAIN = 'venmo.com'
DOMAIN_KEY_SELECTOR = 'lycwyfwp74k6gitv7a7jiergkl3mgkrg'
DOMAIN_KEY_STORED_ON_CONTRACT = 'p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCMh6czdzpSrMH7a5nxQ867R2FqeEkoDdSUszWVL2/06iGLMI4X/mOF23IW31hWBsb5YGkm7vHEwXVltWYpSf1mVGuvqIIyXOb77tOPtVdgkvyfko/z7uUgTT509QYbo3KQyBj6geojrGZF6GN0isLIXxeE11XCz9yKmdh8JK4bAQIDAQAB'
NAME_PATTERN = r"^[A-Z][a-z'’-]+\s([A-Z][a-z'’-]+\s?)+$"
SEND_TO_MERCHANT_EMAIL_BODY_SUBSTR = r"""As an obl=\s*
igor of this payment, PayPal, Inc\. \(855-812-4430\) is liable for non-deliver=\s*
y or delayed delivery of your funds\."""

FROM_EMAIL_ADDRESS = "From: Venmo <venmo@venmo.com>"
EMAIL_SUBJECT = "Subject: You paid (.+?) \$(.+)"
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-venmo-0.1.2-testing-4'
STUB_NAME = 'zkp2p-modal-venmo-0.1.2-staging'

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


Error = Errors()


def alert_on_slack(error_code, email_raw_content="", log_subject=False):

    error_message = Error.get_error_message(error_code)
    msg = f'Alert: {error_message}. Stub: {STUB_NAME}. Docker image: {DOCKER_IMAGE_NAME}'
    
    response = upload_file_to_slack(
        CHANNEL_ID,
        SLACK_TOKEN,
        msg,
        {'file': email_raw_content}
    )
    return response.status_code

def validate_email(email_raw_content):

    # validate domain key
    domain_key = fetch_domain_key(DOMAIN, DOMAIN_KEY_SELECTOR)
    if domain_key is None or domain_key == "" or domain_key != DOMAIN_KEY_STORED_ON_CONTRACT:
        error_code = Error.ErrorCodes.INVALID_DOMAIN_KEY
        alert_on_slack(error_code)
        return False, error_code

    # Validate the DKIM signature
    if not validate_dkim(email_raw_content):
        error_code = Error.ErrorCodes.DKIM_VALIDATION_FAILED
        alert_on_slack(error_code, email_raw_content)
        return False, error_code

    # Ensure the email is from the domain
    if not re.search(fr'{FROM_EMAIL_ADDRESS}', email_raw_content):
        error_code = Error.ErrorCodes.INVALID_FROM_ADDRESS
        alert_on_slack(error_code, email_raw_content)
        return False, error_code
    
    # Ensure the email is a send email
    if not re.search(fr'{EMAIL_SUBJECT}', email_raw_content):
        error_code = Error.ErrorCodes.INVALID_EMAIL_SUBJECT
        alert_on_slack(error_code, email_raw_content, log_subject=True)
        return False, error_code
    
    # Ensure the email is not a send to merchant email
    if re.search(SEND_TO_MERCHANT_EMAIL_BODY_SUBSTR, email_raw_content):
        error_code = Error.ErrorCodes.INVALID_EMAIL
        alert_on_slack(error_code, email_raw_content, log_subject=True)
        return False, error_code

    return True, ""

# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./venmo/.env.example', './venmo/.env')
print("env crednetials", env_credentials)


# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    DOCKER_IMAGE_NAME, 
    add_python="3.11"
).pip_install_from_requirements("requirements.txt")
stub = modal.Stub(name=STUB_NAME, image=image)
stub['credentials_secret'] = modal.Secret.from_dict(env_credentials)


# ----------------- API -----------------

@stub.function(cpu=48, memory=16000, secret=stub['credentials_secret'])
@modal.web_endpoint(method="POST")
def genproof_email(email_data: Dict):

    email_raw_data = email_data["email"]
    payment_type = email_data["payment_type"]
    circuit_type = email_data["circuit_type"]
    intent_hash = email_data["intent_hash"]
    
    nonce = int(sha256_hash(email_raw_data), 16)

    if payment_type == "venmo":
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.INVALID_PAYMENT_TYPE)
        )

    if circuit_type == "send" or circuit_type == "registration":
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.INVALID_CIRCUIT_TYPE)
        )

    # Validate email
    valid_email, error_code = validate_email(email_raw_data)
    if not valid_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(error_code)
        )
    
    # Write file to local
    write_file_to_local(email_raw_data, payment_type, circuit_type, str(nonce))

    # Prove
    run_prove_process(payment_type, circuit_type, str(nonce), intent_hash, "true")

    # Read the proof from local
    proof, public_values = read_proof_from_local(payment_type, circuit_type, str(nonce))

    if proof == "" or public_values == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=Error.get_error_response(Error.ErrorCodes.PROOF_GEN_FAILED)
        )

    # Construct a HTTP response
    response = {
        "proof": proof,
        "public_values": public_values
    }

    return response

