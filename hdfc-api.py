import modal
import re
import boto3
import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from typing import Dict
from utils import fetch_domain_key, \
    validate_dkim, \
    sha256_hash, \
    upload_file_to_slack, \
    replace_message_id_with_x_google_original_message_id, \
    read_proof_from_local, \
    write_file_to_local, \
    prove_email, \
    read_env_credentials
from errors import Errors

load_dotenv()       # Load environment variables from .env file

# --------- VALIDATE EMAIL ------------

DOMAIN = 'hdfcbank.net'
DOMAIN_KEY_SELECTOR = 'acls01'  
DOMAIN_KEY_STORED_ON_CONTRACT = 'p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVuCsG1YQI5vudtUECLUc6nd3rwoD7vb/FZy4jQe5I5tnMIaxQ9jDMOmi0Lf9W62wpHJeZRGKgkMR6cx0voWkTnGDxKiDBajSwjP0EoIlQFTldzN7/XjXVANlHS0N4lWCEngPxmIwfCexXr6prxhjthqDeOryhJUvuMlXc8M0iYVm/Bt4aQi0bVXixBBY4NCY1YJH6ZJBKyPwOmuX'
NAME_PATTERN = r"^[A-Z][a-z'’-]+\s([A-Z][a-z'’-]+\s?)+$"
TEMPLATE = r"""
"""
FROM_EMAIL_ADDRESS = "From: HDFC Bank InstaAlerts <alerts@hdfcbank.net>"
EMAIL_SUBJECT = "Subject: =\?UTF-8\?q\?=E2=9D=97_You_have_done_a_UPI_txn\._Check_details\!\?="
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-upi-0.1.2-testing-1'
STUB_NAME = 'zkp2p-modal-upi-0.1.2-staging'

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
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
    # Modify this to support multiple domain keys
    # domain_key = fetch_domain_key(DOMAIN, DOMAIN_KEY_SELECTOR)
    # if domain_key is None or domain_key == "" or domain_key != DOMAIN_KEY_STORED_ON_CONTRACT:
    #     error_code = Error.ErrorCodes.INVALID_DOMAIN_KEY
    #     alert_on_slack(error_code)
    #     return False, error_code
    
    email_raw_content = replace_message_id_with_x_google_original_message_id(email_raw_content)

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

    return True, ""

# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials()
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

    if payment_type == "hdfc":
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
    proof, public_values = prove_email(payment_type, circuit_type, str(nonce), intent_hash, "true")

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

# ---------------- Run local (inside Docker) or serve and hit the APi -----------------

TEST_PAYMENT_TYPE = os.getenv("TEST_PAYMENT_TYPE")
TEST_CIRCUIT_TYPE = os.getenv("TEST_CIRCUIT_TYPE")
TEST_EMAIL_PATH = os.getenv("TEST_EMAIL_PATH")
MODAL_ENDPOINT = os.getenv("MODAL_ENDPOINT")
TEST_LOCAL_RUN = False
TEST_ENDPOINT = True

# confirm only one test is true
if TEST_LOCAL_RUN + TEST_ENDPOINT != 1:
    raise Exception("Only one test should be true")

if __name__ == "__main__":
    
    # Read an email file
    with open(TEST_EMAIL_PATH, 'r') as file:
        email = file.read()

    # Construct the email data
    email_data = {
        "payment_type": TEST_PAYMENT_TYPE,
        "circuit_type": TEST_CIRCUIT_TYPE,
        "email": email,
        "intent_hash": "12345"
    }
    print(
        "Payment Type: ", email_data['payment_type'], 
        "Circuit Type: ", email_data['circuit_type']
    )

    if TEST_LOCAL_RUN:
        # Call the prove_email function
        response = genproof_email.local(email_data)
        print(response)
    
    elif TEST_ENDPOINT:
        # call the endpoint
        import requests
        import json
        import time
        start = time.time()
        response = requests.post(MODAL_ENDPOINT, json=email_data)
        end = time.time()
        print("Time taken: ", end - start)
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.text)
    
    else:
        pass