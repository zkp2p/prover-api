import modal
import json
import os
import hashlib
from dotenv import load_dotenv
import binascii
from fastapi import HTTPException, status
from typing import Dict

from utils.errors import Errors
from utils.alert import AlertHelper
from utils.tlsp_proof_verifier import TLSPProofVerifier
from utils.env_utils import read_env_credentials

load_dotenv('./basicenv')

# --------- INITIALIZE HELPERS ------------

DOMAIN = 'localhost'
DOCKER_IMAGE_NAME = '0xsachink/zkp2p:modal-tlsp-verifier-v0.1.0-staging'
STUB_NAME = 'zkp2p-tickets-verifier'

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

Error = Errors()
alert_helper = AlertHelper(Error, STUB_NAME, DOCKER_IMAGE_NAME)
alert_helper.init_slack(SLACK_TOKEN, CHANNEL_ID)


# ----------- ENV VARIABLES ------------ (Todo: Clean this)

env_credentials = read_env_credentials('./tickets/.env.example', './tickets/.env')
print("env_credentials", env_credentials)

# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    DOCKER_IMAGE_NAME, 
    add_python="3.11"
).pip_install_from_requirements("./tickets/requirements.txt")
stub = modal.Stub(name=STUB_NAME, image=image)
credentials_secret = modal.Secret.from_dict(env_credentials)

# ----------------- REGEXES -----------------


host_regex_pattern = r"host: ([\w\.-]+)" # Host

response_regexes_config = [
    # Recv data regexes
    (r'o, ([a-z]+) world!', 'string'),
]

def get_regex_patterns(config):
    return [t[0] for t in config]

def get_regex_target_types(config):
    return [t[1] for t in config]

regex_patterns_map = {
    "response": get_regex_patterns(response_regexes_config),
}

regex_target_types = {
    "response": get_regex_target_types(response_regexes_config),
}

error_codes_map = {
    "response": Error.ErrorCodes.TLSN_WISE_INVALID_TRANSFER_VALUES,     # wrong error type
}

# --------- CUSTOM POST PROCESSING ------------ 


def hex_string_to_bytes(hex_string):
    return binascii.unhexlify(hex_string)

def post_processing_public_values(pub_values, regex_types, circuit_type, proof_data):
    # Post processing public values
    local_target_types = regex_types.get(circuit_type, []).copy()

    # Append hashed notary key and type
    notary_pubkey = proof_data["attester_key"]
    notary_pubkey_hashed = hashlib.sha256(notary_pubkey.encode('utf-8')).hexdigest()
    pub_values.append(int(notary_pubkey_hashed, 16))
    local_target_types.append('uint256')

    return pub_values, local_target_types

# ----------------- API -----------------

def clean_public_key(encoded_key):
    return encoded_key.replace("\\n", "\n")

@stub.function(cpu=48, memory=16000, secrets=[credentials_secret]) 
@modal.web_endpoint(method="POST")
def verify_proof(proof_data: Dict):
    return core_verify_proof(proof_data)

def core_verify_proof(proof_data):

    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]

    # Circuit outputs (We will have to consume two proofs)
    # One for request, other for response
    snark_proof = proof_data["snark_proof"]
    ciphertext = proof_data["ciphertext"]
    plaintext = proof_data["plaintext"]
    
    # Proxy API outputs
    attestation = proof_data["attestation"]
    attested_request_ciphertext = proof_data["attested_request_ciphertext"]
    attested_response_ciphertext = proof_data["attested_response_ciphertext"]
    attester_key = proof_data["attester_key"]

    # Start index and end index in response ciphertext that 
    # needs to be searched for in ciphertext
    start_index = proof_data["start_index"]
    end_index = proof_data["end_index"]

    # Instantiate the TLSN proof verifier
    tlsn_proof_verifier = TLSPProofVerifier(
        payment_type=payment_type,
        circuit_type=circuit_type,
        
        attester_key=attester_key,
        attestation=attestation,
        attested_request_ciphertext=attested_request_ciphertext,
        attested_response_ciphertext=attested_response_ciphertext,
        
        ciphertext=ciphertext,
        plaintext=plaintext,
        start_index=start_index,
        end_index=end_index,
        
        regex_patterns_map=regex_patterns_map,
        regex_target_types=regex_target_types,
        error_codes_map=error_codes_map
    )

    if circuit_type not in regex_patterns_map.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.INVALID_CIRCUIT_TYPE)
        )

    # Verify proof
    print('Going to verify proof')
    snark_verify_error = tlsn_proof_verifier.verify_tlsn_proof(snark_proof)
    if snark_verify_error != "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(Error.ErrorCodes.TLSN_PROOF_VERIFICATION_FAILED)
        )

    # Extract required values from session data
    # TODO: COULD ALSO USE THE INDICES HERE.
    extract_data = bytes.fromhex(plaintext).decode('ascii', errors='ignore')

    public_values, valid_values, error_code = tlsn_proof_verifier.extract_regexes(extract_data)
    if not valid_values:
        alert_helper.alert_on_slack(error_code, plaintext + proof_data)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=Error.get_error_response(error_code)
        )

    # Logging
    print('Public Values:', public_values)
    print('Value types:', tlsn_proof_verifier.regex_target_types)

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
