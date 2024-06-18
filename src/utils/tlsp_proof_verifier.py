import os
import subprocess
from utils.helpers import sha256_hash
from utils.file_utils import (
    write_tlsn_proof_to_local, 
    get_tlsn_proof_file_path, 
)
from utils.regex_helpers import extract_regex_values
from utils.sign import sign_values_with_private_key
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

def deserialize_public_key_from_pem(pem_data):
    """
    Deserialize the public key from PEM format.
    """
    public_key = serialization.load_pem_public_key(
        pem_data.encode('utf-8'),
        backend=default_backend()  # This can be omitted in newer versions of cryptography
    )
    return public_key

def verify_signature(public_key, data, signature):
    """Verify a signature using a public key."""
    try:
        public_key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False


class TLSPProofVerifier:
    def __init__(
            self,
            payment_type: str,
            circuit_type: str,
            attester_key: str,
            attestation: str,
            attested_request_ciphertext: str,
            attested_response_ciphertext: str,
            ciphertext: str,
            plaintext: str,
            start_index: int,
            end_index: int,
            regex_patterns_map: dict,
            regex_target_types: dict,
            error_codes_map: dict
        ):
        self.payment_type = payment_type
        self.circuit_type = circuit_type
        
        self.attester_key = attester_key
        self.attestation=attestation
        self.attested_request_ciphertext=attested_request_ciphertext
        self.attested_response_ciphertext=attested_response_ciphertext
        
        self.ciphertext=ciphertext
        self.plaintext=plaintext
        self.start_index = int(start_index)
        self.end_index = int(end_index)

        self.regex_patterns_map = regex_patterns_map
        self.regex_target_types = regex_target_types
        self.error_codes_map = error_codes_map
        self.base_path = os.environ.get('CUSTOM_PROVER_API_PATH', "/root/prover-api")

    def extract_regexes(self, data):
        regex_patterns = self.regex_patterns_map.get(self.circuit_type, [])
        public_values = extract_regex_values(data, regex_patterns)

        valid = len(public_values) == len(regex_patterns) and all(val != 'null' and val != "" for val in public_values)

        if not valid:
            return [], False, self.error_codes_map[self.circuit_type]

        return public_values, valid, ""

    def verify_tlsn_proof(self, snark_proof):
        nonce = int(sha256_hash(snark_proof), 16)

        # Write file to local
        write_tlsn_proof_to_local(snark_proof, self.payment_type, self.circuit_type, str(nonce))

        print('Performing sig verification')
        if not self.run_sig_verify(nonce):
            return "Failed signature verification"

        # Verify the notaries signature on encoded data using the rust verifier
        print('Running verify process')
        proof_verified = self.run_proof_verify_process(str(nonce))

        # Exit early if error is found
        if not proof_verified:
            return "Failed SNARK proof verification"
        
        if not self.run_ciphetext_equality_verify():
            return "Failed ciphertext equality verification"

        return ""

    def run_sig_verify(self, nonce):
        msg = bytes.fromhex(self.attested_request_ciphertext) + bytes.fromhex(self.attested_response_ciphertext)
        pub_key = deserialize_public_key_from_pem(self.attester_key)
        signature_bytes = bytes.fromhex(self.attestation)
        return verify_signature(pub_key, msg, signature_bytes)

    def run_proof_verify_process(self, nonce):
        tlsn_proof_file_path = get_tlsn_proof_file_path(self.payment_type, self.circuit_type, nonce)
        print(tlsn_proof_file_path)
        result = subprocess.run(
            [
                'ts-node',
                f"{self.base_path}/tlsp-verifier/index.ts",
                tlsn_proof_file_path,
                self.plaintext,
                self.ciphertext
            ],
            capture_output=True,
            text=True
        )
        # Printing the output
        print('Result', result.stdout)
        print('Error', result.stderr)
        return True if result.returncode == 0 else False
    
    def run_ciphetext_equality_verify(self):
        # Check if the start and end indices are within the bounds of both strings
        if self.start_index < 0 or self.end_index > len(self.ciphertext):
            raise ValueError("Start and end indices must be within the bounds of both strings.")

        # Extract the substrings
        substring1 = self.ciphertext[self.start_index:self.end_index]
        print('Looking for', substring1, 'in response ciphertext')
        return substring1 in self.attested_response_ciphertext


    def sign_and_serialize_values(self, public_values, target_types):
        signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values, target_types)
        serialized_values = [str(v) for v in public_values]

        return signature, serialized_values

