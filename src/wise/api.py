import modal
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from typing import Dict

from utils.errors import Errors
from utils.alert import AlertHelper
from utils.verify import verify_tlsn_proof
from utils.env_utils import read_env_credentials


load_dotenv('./env')       # Load environment variables from .env file

# --------- INITIALIZE HELPERS ------------

DOMAIN = 'wise.com'
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-wise-verifier-0.2.5-testing-1' #'0xsachink/zkp2p:modal-wise-0.2.5'      # Add verifier to the docker name
STUB_NAME = 'zkp2p-wise-verifier-0.2.5'

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

Error = Errors()
alert_helper = AlertHelper(Error, STUB_NAME, DOCKER_IMAGE_NAME)
alert_helper.init_slack(SLACK_TOKEN, CHANNEL_ID)


# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./wise/.env.example', './wise/.env')
print("env crednetials", env_credentials)

# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    DOCKER_IMAGE_NAME, 
    add_python="3.11"
).pip_install_from_requirements("./wise/requirements.txt")
stub = modal.Stub(name=STUB_NAME, image=image)
stub['credentials_secret'] = modal.Secret.from_dict(env_credentials)


# --------- SANITY CHECK INPUT ----------


def validate_proof(proof_raw):

    # Validate all the values here before invoking the wasm verifier to verify registration. 
    # Can we decode in python??? :think:


    # TODO: VERIFY EMPTY KEYS, AND ENSURE NOTE ISN'T USED USED TO ATTACK VERFIFICATION.


    # Todo: What sanity check should we perform here?
    # Should we check for any malcicious injected data in the proof here?
    # Anything that is not checked on either the Smart contract or by the verifier 
    # should be checked here.

    return True, ""


# ----------------- REGEXES -----------------

# Emulating zk-regex config files in python

get_endpoint_regex_pattern = r"GET (https:\/\/wise\.com\/[^\s]+)" # Get endpoint
post_endpoint_regex_pattern = r"POST (https:\/\/wise\.com\/[^\s]+)" # Post endpoint
endpoint_type_regex_pattern = r"(GET|POST|PUT|DELETE) https:\/\/wise\.com" # Endpoint type
host_regex_pattern = r"host: ([\w\.-]+)" # Host

send_regexes = [
    get_endpoint_regex_pattern,
    endpoint_type_regex_pattern,
    host_regex_pattern,
]

send_keys = [
    "id",
    "profileId",
    "targetRecipientId",
    "targetCurrency",
    "state",
    ["stateHistory", "date"]        # Fix this to extract date corresponding to final outgoing payment sent
]

registration_regexes = [
    get_endpoint_regex_pattern,
    endpoint_type_regex_pattern,
    host_regex_pattern,
]

registration_keys = [
    # r'"recipientId":\s*(\d+)',  # recipientId
    # r'"active":\s*(true|false)',  # active
    # r'"eligible":\s*(true|false)'  # eligible
]

# ----------------- API -----------------

@stub.function(cpu=48, memory=16000, secret=stub['credentials_secret'])
@modal.web_endpoint(method="POST")
def verify_proof(proof_data: Dict):

    proof_raw_data = proof_data["proof"]
    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]
    
    if payment_type == "wise":
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

    # Validate proof structure
    valid_proof, error_code = validate_proof(proof_raw_data)
    if not valid_proof:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(error_code)
        )
    
    # Verify proof
    signature, public_values = verify_tlsn_proof(proof_data, send_regex_patterns, registration_regex_patterns)
    if signature == "" or public_values == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=Error.get_error_response(Error.ErrorCodes.TLSN_PROOF_VERIFICATION_FAILED)
        )

    response = {
        "proof": signature,
        "public_values": public_values
    }

    return response

