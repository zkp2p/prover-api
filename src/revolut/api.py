import modal
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from typing import Dict
import json

from utils.errors import Errors
from utils.alert import AlertHelper
from utils.tlsn_proof_verifier import TLSNProofVerifier
from utils.env_utils import read_env_credentials
from utils.sign import encode_and_hash

load_dotenv('./env')

# --------- INITIALIZE HELPERS ------------

DOMAIN = 'api.revolut.com'
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-wise-verifier-0.2.5-testing-1'
STUB_NAME = 'zkp2p-revolut-staging-verifier-0.2.5'

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

Error = Errors()
alert_helper = AlertHelper(Error, STUB_NAME, DOCKER_IMAGE_NAME)
alert_helper.init_slack(SLACK_TOKEN, CHANNEL_ID)


# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./revolut/.env.example', './revolut/.env')
print("env_credentials", env_credentials)

# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    DOCKER_IMAGE_NAME, 
    add_python="3.11"
).pip_install_from_requirements("./revolut/requirements.txt")
stub = modal.Stub(name=STUB_NAME, image=image)
credentials_secret = modal.Secret.from_dict(env_credentials)

# ----------------- REGEXES -----------------

# We can't convert the response to json and then index out the values using keys
# because the json structure may no longer be preserved upon redaction. Also, when
# notarizing websites we wouldn't be receiving json responses. 
# In contrast, regexes should work for all cases. Also, the same regexes can later
# be reused inside circuits
host_regex_pattern = r"host: ([\w\.-]+)" # Host

transfer_regexes_config = [
    # Send data regexes
    (r'^(GET https://app.revolut.com/api/retail/transaction/([a-fA-F0-9-]+))', 'string'),
    (host_regex_pattern, 'string'),

    # Recv data regexes
    (r'"id":"([a-fA-F0-9-]+)","legId":"([a-fA-F0-9-]+)","type":"TRANSFER","state":"COMPLETED","startedDate":(\d+),"updatedDate":(\d+)', 'string'),  # Transaction ID
    (r'"code":"(\w+)","account":{"id":"([a-fA-F0-9-]+)","type":"CURRENT"}},"localisedDescription":{"key":"transaction.description.generic.name","params":\[[X]+\]', 'string'),  # Target RevID
    (r'"amount":([\d.-]+),"fee":(\d+),"balance":([X]+),"description":([X]+),', 'string'),  # Target Amount
    (r'"currency":"([A-Z]{3})","amount":([\d.-]+),"fee":(\d+),"balance":([X]+),"description":([X]+),', 'string'),  # Target Currency
    (r'"type":"TRANSFER","state":"(\w+)","startedDate":(\d+),"updatedDate":(\d+)', 'string'),  # State
    (r'"completedDate":(\d+),"createdDate":(\d+),"currency":"([A-Z]{3})","amount":([\d.-]+),"fee":(\d+),"balance":([X]+),"description":([X]+),', 'string') # Unix date
]

registration_individual_id_regexes_config = [
    # Send data regexes
    (r'^(GET https://app.revolut.com/api/retail/user/current)', 'string'),
    (host_regex_pattern, 'string'),

    # Recv data regexes
    (r'"code":"(\w+)","kyc":"PASSED","underReview":false', 'string')
]

def get_regex_patterns(config):
    return [t[0] for t in config]

def get_regex_target_types(config):
    return [t[1] for t in config]

regex_patterns_map = {
    "transfer": get_regex_patterns(transfer_regexes_config),
    "registration_individual_id": get_regex_patterns(registration_individual_id_regexes_config)
}

regex_target_types = {
    "transfer": get_regex_target_types(transfer_regexes_config),
    "registration_individual_id": get_regex_target_types(registration_individual_id_regexes_config)
}

error_codes_map = {
    "transfer": Error.ErrorCodes.TLSN_WISE_INVALID_TRANSFER_VALUES,
    "registration_individual_id": Error.ErrorCodes.TLSN_WISE_INVALID_PROFILE_REGISTRATION_VALUES
}

# --------- CUSTOM POST PROCESSING ------------ 

def post_processing_public_values(pub_values, regex_types, circuit_type, proof_data):
    # Post processing public values
    local_target_types = regex_types.get(circuit_type, []).copy()

    if circuit_type == "transfer":
        pub_values.append(int(proof_data["intent_hash"]))
        local_target_types.append('uint256')

    if circuit_type == "registration_individual_id":
        # Todo: find a more cleaner way to do it
        individual_id = pub_values[-1]
        out_hash = encode_and_hash([individual_id], ['string'])
        pub_values[-1] = str(int(out_hash, 16))

        pub_values.append(proof_data["user_address"])
        local_target_types.append('address')

    return pub_values, local_target_types

# ----------------- API -----------------

@stub.function(cpu=48, memory=16000, secrets=[credentials_secret]) 
@modal.web_endpoint(method="POST")
def verify_proof(proof_data: Dict):
    return core_verify_proof(proof_data)

def core_verify_proof(proof_data):

    proof_raw_data = proof_data["proof"]
    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]

    # Instantiate the TLSN proof verifier
    tlsn_proof_verifier = TLSNProofVerifier(
        payment_type=payment_type,
        circuit_type=circuit_type,
        regex_patterns_map=regex_patterns_map,
        regex_target_types=regex_target_types,
        error_codes_map=error_codes_map
    )

    if payment_type == "revolut":
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

    # Verify proof
    send_data, recv_data, tlsn_verify_error = tlsn_proof_verifier.verify_tlsn_proof(proof_raw_data)
    if tlsn_verify_error != "" or send_data == "" or recv_data == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.TLSN_PROOF_VERIFICATION_FAILED)
        )

    # Extract required values from session data
    public_values, valid_values, error_code = tlsn_proof_verifier.extract_regexes(send_data, recv_data)
    if not valid_values:
        alert_helper.alert_on_slack(error_code, send_data + recv_data)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(error_code)
        )

    # Custom post processing public values defined above
    post_processed_public_values, post_processed_target_types = post_processing_public_values(
        public_values,
        tlsn_proof_verifier.regex_target_types,
        circuit_type,
        proof_data
    )
    
    # Logging
    print('Public Values:', post_processed_public_values)
    print('Value types:', post_processed_target_types)

    # Sign on public values using verifier private key
    signature, serialized_values = tlsn_proof_verifier.sign_and_serialize_values(post_processed_public_values, post_processed_target_types)

    response = {
        "proof": signature,
        "public_values": serialized_values
    }

    return response
