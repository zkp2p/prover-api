import os
import re
import time
import modal
import requests
from dotenv import load_dotenv
from fastapi import HTTPException, status
from typing import Dict

from utils.helpers import fetch_domain_key, validate_dkim, sha256_hash
from utils.prove import run_prove_process
from utils.errors import Errors
from utils.env_utils import read_env_credentials
from utils.file_utils import write_file_to_local, read_proof_from_local
from utils.slack_utils import upload_file_to_slack

load_dotenv('./env')       # Load environment variables from .env file

# --------- VALIDATE EMAIL ------------

DOMAIN = 'info.garantibbva.com.tr'
DOMAIN_KEYS = [
    {
        'selector': 'BulkMailSelector1',
        'key': 'p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVuCsG1YQI5vudtUECLUc6nd3rwoD7vb/FZy4jQe5I5tnMIaxQ9jDMOmi0Lf9W62wpHJeZRGKgkMR6cx0voWkTnGDxKiDBajSwjP0EoIlQFTldzN7/XjXVANlHS0N4lWCEngPxmIwfCexXr6prxhjthqDeOryhJUvuMlXc8M0iYVm/Bt4aQi0bVXixBBY4NCY1YJH6ZJBKyPwOmuXUI/p6aFkZm4qY+ymlFQuAgb+jGqd+q/t/gKCBH4M+muCknyA7/gMspMbzPg56WaX/0B0B7RmCmd5FVrDy/XPUQa3kKn78dALQrriVEwnGjggBC2rHAUbzyMeiuWS8+LZTcyeQIDAQAB'
    }
]
SELECTORS = [dk['selector'] for dk in DOMAIN_KEYS]
# NAME_PATTERN = r"^[A-Z][a-z'’-]+\s([A-Z][a-z'’-]+\s?)+$"
FROM_EMAIL_ADDRESS = "From: Garanti BBVA <garanti@info.garantibbva.com.tr>"
EMAIL_SUBJECT = "Subject: Para Transferi Bilgilendirmesi"
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-garanti-0.2.4-staging-testing'
STUB_NAME = 'zkp2p-modal-garanti-0.2.4-staging'

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
    
    # Extract the selector from the email
    # Selector is present in this form in the email 's=BulkMailSelector1; c=simple/simple;'
    match = re.search(r's=(.*?);[\s]*c=simple/simple', email_raw_content)

    # Validate selector
    if not match or match.group(1) not in SELECTORS:
        error_code = Error.ErrorCodes.INVALID_SELECTOR
        alert_on_slack(error_code, email_raw_content)
        return False, error_code
    
    # Validate domain key
    # DNS query takes time and slows down the modal. Since this check is already done on the client, we can skip it.
    # domain_key = fetch_domain_key(DOMAIN, selector)
    # print("Fetched domain_key", domain_key)
    # if domain_key == "" or domain_key is None or domain_key != DOMAIN_KEYS[SELECTORS.index(selector)]['key']:
    #     error_code = Error.ErrorCodes.INVALID_DOMAIN_KEY
    #     alert_on_slack(error_code, email_raw_content)
    #     return False, error_code
    
    # Validate the DKIM signature
    if not validate_dkim(email_raw_content):
        error_code = Error.ErrorCodes.DKIM_VALIDATION_FAILED
        alert_on_slack(error_code, email_raw_content)
        return False, error_code

    return True, ""

# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./garanti/.env.example', './garanti/.env')
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

    if payment_type == "garanti":
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.INVALID_PAYMENT_TYPE)
        )

    if circuit_type == "send" or circuit_type == "registration" or circuit_type == "body_suffix_hasher":
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