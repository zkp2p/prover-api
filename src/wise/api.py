import modal
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from typing import Dict

from utils.helpers import fetch_domain_key, validate_dkim, sha256_hash
from utils.verify import run_verify_process, extract_values_from_response
from utils.errors import Errors
from utils.env_utils import read_env_credentials
from utils.file_utils import write_tlsn_proof_to_local, read_tlsn_verify_output_from_local
from utils.slack_utils import upload_file_to_slack
from utils.sign import sign_values_with_private_key

load_dotenv('./env')       # Load environment variables from .env file

# --------- VALIDATE EMAIL ------------

DOMAIN = 'wise.com'
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-wise-verifier-0.2.5-testing-1' #'0xsachink/zkp2p:modal-wise-0.2.5'      # Add verifier to the docker name
STUB_NAME = 'zkp2p-wise-verifier-0.2.5'

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')


Error = Errors()


def alert_on_slack(error_code, file_payload="", log_subject=False):

    error_message = Error.get_error_message(error_code)
    msg = f'Alert: {error_message}. Stub: {STUB_NAME}. Docker image: {DOCKER_IMAGE_NAME}'
    
    response = upload_file_to_slack(
        CHANNEL_ID,
        SLACK_TOKEN,
        msg,
        {'file': file_payload}
    )
    return response.status_code


def validate_proof(proof_raw):
    return True, ""

# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./wise/.env.example', './wise/.env')
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
def verify_proof(proof_data: Dict):

    proof_raw_data = proof_data["proof"]
    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]
    intent_hash = proof_data["intent_hash"]
    print('proof_raw_data', proof_raw_data)
    
    nonce = int(sha256_hash(proof_raw_data), 16)

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

    # Validate proof
    print('validating proof')
    valid_proof, error_code = validate_proof(proof_raw_data)
    if not valid_proof:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(error_code)
        )
    print('proof is valid')
    
    # Write file to local
    print('writing tlsn proof to local')
    write_tlsn_proof_to_local(proof_raw_data, payment_type, circuit_type, str(nonce))
    print('wrote tlsn proof to local')

    # Verify the notarized session
    print('verifying the notarized session')
    run_verify_process(payment_type, circuit_type, str(nonce))

    sent_data, recv_data = read_tlsn_verify_output_from_local(payment_type, circuit_type, str(nonce))
    print('recv_data', recv_data)

    # If verification passes; then extract out relevant data from the response and sign on it
    keys = [
        'id',
        'targetAccount',
        'targetCurrency',
        'targetValue',
        'hasActiveIssues',
        'status'
    ]
    print('searching for public values in the response')
    public_values = extract_values_from_response(recv_data, keys)

    public_values.append(intent_hash)
    print(public_values)

    # Sign public values
    signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values)
    print(signature, 'signature')

    if signature == "" or public_values == "":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=Error.get_error_response(Error.ErrorCodes.PROOF_GEN_FAILED)
        )

    # Construct a HTTP response
    response = {
        "proof": signature,
        "public_values": public_values
    }

    return response

