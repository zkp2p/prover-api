import modal
import re
import boto3
import requests
import hashlib
import subprocess
import os
from dotenv import load_dotenv
from enum import Enum
from fastapi import FastAPI, HTTPException, status
from typing import Dict
from utils import fetch_domain_key, validate_dkim, match_and_sub, sha256_hash, upload_file_to_slack


load_dotenv()       # Load environment variables from .env file

# Paths
incoming_eml_file_path = "/root/prover-api/received_eml/[payment_type]_[circuit_type]_[nonce].eml"
proof_file_path = "/root/prover-api/proofs/rapidsnark_proof_[payment_type]_[circuit_type]_[nonce].json"
public_values_file_path = "/root/prover-api/proofs/rapidsnark_public_[payment_type]_[circuit_type]_[nonce].json"


# --------- VALIDATE EMAIL ------------

DOMAIN = 'hdfcbank.net'
DOMAIN_KEY_SELECTOR = 'acls01'
DOMAIN_KEY_STORED_ON_CONTRACT = 'p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnVuCsG1YQI5vudtUECLUc6nd3rwoD7vb/FZy4jQe5I5tnMIaxQ9jDMOmi0Lf9W62wpHJeZRGKgkMR6cx0voWkTnGDxKiDBajSwjP0EoIlQFTldzN7/XjXVANlHS0N4lWCEngPxmIwfCexXr6prxhjthqDeOryhJUvuMlXc8M0iYVm/Bt4aQi0bVXixBBY4NCY1YJH6ZJBKyPwOmuX'
NAME_PATTERN = r"^[A-Z][a-z'’-]+\s([A-Z][a-z'’-]+\s?)+$"
TEMPLATE = r"""
"""

FROM_EMAIL_ADDRESS = "From: HDFC Bank InstaAlerts <alerts@hdfcbank.net>"
EMAIL_SUBJECT = "Subject: =?UTF-8?q?=E2=9D=97_You_have_done_a_UPI_txn._Check_details!?="
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-upi-0.1.1'
STUB_NAME = 'zkp2p:modal-upi-0.1.1-testing'

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


class Errors:

    class ErrorCodes(Enum):
        INVALID_CIRCUIT_TYPE = 1
        NOT_VALID_EMAIL_TYPE = 2
        INVALID_DOMAIN_KEY = 3
        DKIM_VALIDATION_FAILED = 4
        NOT_FROM_DOMAIN = 5
        INVALID_TEMPLATE = 6
        PROOF_GEN_FAILED = 7
        INVALID_PAYMENT_TYPE = 8

    def __init__(self):
        self.error_messages = {
            self.ErrorCodes.INVALID_EMAIL_TYPE: "Invalid email type",
            self.ErrorCodes.NOT_VALID_EMAIL_TYPE: "Email is not a send email",
            self.ErrorCodes.INVALID_DOMAIN_KEY: "❗️Domain key might have changed❗️",
            self.ErrorCodes.DKIM_VALIDATION_FAILED: "DKIM validation failed",
            self.ErrorCodes.NOT_FROM_DOMAIN: "Email is not from Domain",
            self.ErrorCodes.INVALID_TEMPLATE: "❗️Email does not have the right template❗️",
            self.ErrorCodes.PROOF_GEN_FAILED: "Proof generation failed"
        }

    def get_error_message(self, error_code):
        return self.error_messages[error_code]
    
    def get_error_response(self, error_code):
        return {
            "code": error_code.value,
            "message": self.get_error_message(error_code)
        }


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
        error_code = Error.ErrorCodes.NOT_FROM_DOMAIN
        alert_on_slack(error_code, email_raw_content)
        return False, error_code
    
    # Ensure the email is a send email
    if not re.search(fr'{EMAIL_SUBJECT}', email_raw_content):
        error_code = Error.ErrorCodes.NOT_VALID_EMAIL_TYPE
        alert_on_slack(error_code, email_raw_content, log_subject=True)
        return False, error_code

    # Ensure the email has the right template
    # match = re.search(TEMPLATE, email_raw_content)
    # if not match:
    #     error_code = Error.ErrorCodes.INVALID_TEMPLATE
    #     alert_on_slack(error_code, email_raw_content, log_subject=True)
    #     return False, error_code

    return True, ""

# --------- AWS HELPER FUNCTIONS ------------

def write_file_to_local(file_contents, payment_type, circuit_type, nonce):
    file_path = incoming_eml_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)
    with open(file_path, 'w') as file:
        file.write(file_contents)
    return file_path


def read_proof_from_local(payment_type, circuit_type, nonce):
    proof = ""
    public_values = ""
    proof_file_name = proof_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)
    public_values_file_name = public_values_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)

    # check if the file exists
    if not os.path.isfile(proof_file_name) or not os.path.isfile(public_values_file_name):
        print("Proof file does not exist")
        return proof, public_values

    with open(proof_file_name, 'r') as file:
        proof = file.read()
    
    with open(public_values_file_name, 'r') as file:
        public_values = file.read()
    
    return proof, public_values



# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_example_path = "./.env.example"
env_credentials = {}
if os.path.isfile(env_example_path):
    def get_variable_names_from_env_file(file_path=env_example_path):
        variable_names = []
        with open(file_path) as file:
            for line in file:
                # Ignore comments and empty lines
                if line.startswith('#') or line.strip() == '':
                    continue
                # Extract variable name (part before the '=' character)
                variable_name = line.split('=')[0].strip()
                variable_names.append(variable_name)
        return variable_names

    # Load additional environment variables from the .env file
    additional_vars = get_variable_names_from_env_file()
    load_dotenv()  # Load environment variables from .env file
    for var_name in additional_vars:
        # If it doesnt start with local
        if not var_name.startswith("LOCAL_"):
            var_value = os.getenv(var_name)
            if var_value is not None:
                # TODO: Make this cleaner; remove all uses of a non local/modal path env var
                env_credentials[var_name] = var_value
                var_name = var_name.replace("MODAL_", "")
                env_credentials[var_name] = var_value

print("env crednetials", env_credentials)


# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    DOCKER_IMAGE_NAME, 
    add_python="3.11"
).pip_install_from_requirements("requirements.txt")
stub = modal.Stub(name=STUB_NAME, image=image)
stub['credentials_secret'] = modal.Secret.from_dict(env_credentials)


def prove_email(payment_type:str, circuit_type:str, nonce: str, intent_hash: str):
    print('Running prove email')
    
    import subprocess 

    # Run the circom proofgen script
    result = subprocess.run(['/root/prover-api/circom_proofgen.sh', payment_type, circuit_type, nonce, intent_hash], capture_output=True, text=True)
    print(result.stdout)
    
    # Read the proof and public values 
    proof, public_values = read_proof_from_local(payment_type, circuit_type, nonce)
    return proof, public_values



# ----------------- API -----------------

@stub.function(cpu=48, memory=16000, secret=stub['credentials_secret'])
@modal.web_endpoint(method="POST")
def genproof_email(email_data: Dict):

    email_raw_data = email_data["email"]
    payment_type = email_data["payment_type"]
    circuit_type = email_data["circuit_type"]
    intent_hash = email_data["intent_hash"]
    
    nonce = int(sha256_hash(email_raw_data), 16)

    if payment_type == "venmo" or payment_type == "hdfc":
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
    proof, public_values = prove_email(payment_type, circuit_type, str(nonce), intent_hash)

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


# ----------------- Modal Inovke -----------------

@stub.local_entrypoint()
def run_modal():

    # Read an email file
    with open('./received_eml/test.eml', 'r') as file:
        email = file.read()

    # Construct the email data
    email_data = {
        "payment_type": "venmo",
        "circuit_type": "send",
        "email": email
    }

    # Call the prove_email function
    response = genproof_email.remote(email_data)
    print(response)

# ---------------- Run local (inside Docker) or serve and hit the APi -----------------

TEST_PAYMENT_TYPE = os.getenv("TEST_PAYMENT_TYPE")
TEST_CIRCUIT_TYPE = os.getenv("TEST_CIRCUIT_TYPE")
TEST_EMAIL_PATH = os.getenv("TEST_EMAIL_PATH")
MODAL_ENDPOINT = os.getenv("MODAL_ENDPOINT")
TEST_LOCAL_RUN = os.getenv("TEST_LOCAL_RUN")
TEST_ENDPOINT = os.getenv("TEST_ENDPOINT")

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