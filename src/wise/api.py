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
from utils.sign import sign_values_with_private_key
from utils.regex_helpers import extract_regex_values

load_dotenv('./env')       # Load environment variables from .env file

# --------- INITIALIZE HELPERS ------------

DOMAIN = 'wise.com'
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-wise-verifier-0.2.5-testing-1'
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

    # Log on modal for debugging
    print(proof_raw)

    # Todo: What sanity check should we perform here?
    # Should we check for any malcicious injected data in the proof here?
    # Anything that is not checked on either the Smart contract or by the verifier 
    # should be checked here.

    return True, ""


# ----------------- REGEXES -----------------

# We can't convert the response to json and then index out the values using keys
# because the json structure may no longer be preserved upon redaction. Also, when
# notarizing websites we wouldn't be receiving json responses. 
# In contrast, regexes should work for all cases. Also, the same regexes can later
# be reused insdie circuits
host_regex_pattern = r"host: ([\w\.-]+)" # Host

transfer_regexes_config = [
    # Send data regexes
    (r'^(GET https://wise\.com/gateway/v3/profiles/(\d+)/transfers)', 'string'),     # Transfer endpoint
    (host_regex_pattern, 'string'),

    # Recv data regexes
    (r'"id":(\d+)', 'string'),  # ID
    (r'"profileId":(\d+)', 'string'),  # Profile Id
    (r'"targetRecipientId":(\d+)', 'string'),  # Target Account
    (r'"targetAmount":([\d.]+)', 'string'),  # Target Amount
    (r'"targetCurrency":"([A-Z]{3})"', 'string'),  # Target Currency
    (r'"state":"(\w+)"', 'string'),  # State
    (r'"state":"OUTGOING_PAYMENT_SENT","date":(\d+)', 'string') # Unix date
]

registration_profile_id_regexes_config = [
    # Send data regexes
    (r'^(POST https://wise\.com/gateway/v1/payments)', 'string'),     # Transfer endpoint,
    (host_regex_pattern, 'string'),
    (r'"profileId":(\d+)', 'string'),

    # Recv data regexes
    (r'"name":"Your Wisetag","description":"@([^"]+)"', 'string')
]

registration_account_id_regexes_config = [
    # Send data regexes
    (r'^(GET https://wise\.com/gateway/v3/profiles/(\d+)/transfers)', 'string'),     # Transfer endpoint,
    (host_regex_pattern, 'string'),

    # Recv data regexes
    (r'"profileId":(\d+)', 'string'),
    (r'"refundRecipientId":(\d+)', 'string')
]

def get_regex_patterns(config):
    return [t[0] for t in config]

def get_regex_target_types(config):
    return [t[1] for t in config]

regex_patterns_map = {
    "transfer": get_regex_patterns(transfer_regexes_config),
    "registration_profile_id": get_regex_patterns(registration_profile_id_regexes_config),
    "registration_account_id": get_regex_patterns(registration_account_id_regexes_config)
}

regex_target_types = {
    "transfer": get_regex_target_types(transfer_regexes_config),
    "registration_profile_id": get_regex_target_types(registration_profile_id_regexes_config),
    "registration_account_id": get_regex_target_types(registration_account_id_regexes_config)
}

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

    if circuit_type not in regex_patterns_map.keys():
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
    send_data, recv_data = verify_tlsn_proof(proof_data)
    if send_data == "" or recv_data == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.TLSN_PROOF_VERIFICATION_FAILED)
        )

    # Extract required values from session data
    data = send_data + recv_data
    regex_patterns = regex_patterns_map.get(circuit_type, [])
    public_values = extract_regex_values(data, regex_patterns)
    if len(public_values) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.TLSN_VALUES_EXTRACTION_FAILED)
        )

    if payment_type == "transfer":
        public_values.append(proof_data["intent_hash"])


    # Sign on payment details using verifier private key
    target_types = regex_target_types.get(circuit_type, [])
    # Logging
    print('Public Values:', public_values)
    print('Value types:', target_types)
    signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values, target_types)

    response = {
        "proof": signature,
        "public_values": public_values
    }

    return response

