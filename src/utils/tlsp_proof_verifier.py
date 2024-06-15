import os
import subprocess
from utils.helpers import sha256_hash
from utils.file_utils import (
    write_tlsn_proof_to_local, 
    get_tlsn_proof_file_path, 
)
from utils.regex_helpers import extract_regex_values
from utils.sign import sign_values_with_private_key
import binascii
import hashlib
from ecdsa import SigningKey, SECP256k1, VerifyingKey


def load_ecdsa_public_key_from_hex(public_key_hex):
    """Load an ECDSA public key from a hex string."""
    try:
        public_key_bytes = binascii.unhexlify(public_key_hex)
        public_key = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
        return public_key
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def sign_message(message, private_key):
    """Sign a message using the provided ECDSA private key."""
    message_hash = hashlib.sha256(message.encode()).digest()
    signature = private_key.sign(message_hash)
    return signature

def verify_signature(message, signature, public_key):
    """Verify the ECDSA signature using the corresponding public key."""
    message_hash = hashlib.sha256(message.encode()).digest()
    return public_key.verify(signature, message_hash)

class TLSPProofVerifier:
    def __init__(
            self,
            payment_type: str,
            circuit_type: str,
            attester_key: str,
            attestation: str,
            attested_ciphertext: str,
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
        self.attested_ciphertext=attested_ciphertext
        self.ciphertext=ciphertext
        self.plaintext=plaintext
        self.start_index = start_index
        self.end_index = end_index

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

    def verify_tlsn_proof(self, proof_raw_data):
        nonce = int(sha256_hash(proof_raw_data), 16)

        # Write file to local
        write_tlsn_proof_to_local(proof_raw_data, self.payment_type, self.circuit_type, str(nonce))

        if not self.run_sig_verify(nonce):
            return "Failed signature verification"

        # Verify the notaries signature on encoded data using the rust verifier
        print('Running verify process')
        result = self.run_proof_verify_process(str(nonce))

        # Exit early if error is found
        if result.stderr != "":
            return result.stderr
        
        if not self.run_ciphetext_equality_verify():
            return "Failed ciphertext equality verification"

        return ""

    def run_sig_verify(self, nonce):
        pub_key = load_ecdsa_public_key_from_hex(self.attester_key)
        return verify_signature(self.attested_ciphertext, self.attestation, pub_key)

    def run_proof_verify_process(self, nonce):
        tlsn_proof_file_path = get_tlsn_proof_file_path(self.payment_type, self.circuit_type, nonce)
        
        result = subprocess.run(
            [
                f"{self.base_path}/tlsp-verifier/lib/verifier",
                tlsn_proof_file_path,
                self.plaintext,
                self.ciphertext
            ],
            capture_output=True,
            text=True
        )
        print('Result', result.stdout)
        return result
    
    def run_ciphetext_equality_verify(self):
        # Check if the start and end indices are within the bounds of both strings
        if self.start_index < 0 or self.end_index > len(self.ciphertext) or self.end_index > len(self.attested_ciphertext):
            raise ValueError("Start and end indices must be within the bounds of both strings.")

        # Extract the substrings
        substring1 = self.ciphertext[self.start_index:self.end_index]
        substring2 = self.attested_ciphertext[self.start_index:self.end_index]
        return substring1 == substring2


    def sign_and_serialize_values(self, public_values, target_types):
        signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values, target_types)
        serialized_values = [str(v) for v in public_values]

        return signature, serialized_values


