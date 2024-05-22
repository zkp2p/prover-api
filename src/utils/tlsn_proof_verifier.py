import os
import subprocess
from utils.helpers import sha256_hash
from utils.file_utils import (
    write_tlsn_proof_to_local, 
    write_notary_pubkey_to_local,
    read_tlsn_verify_output_from_local, 
    get_notary_pubkey_path,
    get_tlsn_proof_file_path, 
    get_tlsn_recv_data_file_path, 
    get_tlsn_send_data_file_path
)
from utils.regex_helpers import extract_regex_values
from utils.sign import sign_values_with_private_key

class TLSNProofVerifier:
    def __init__(
            self,
            notary_pubkey: str,
            payment_type: str,
            circuit_type: str,
            regex_patterns_map: dict,
            regex_target_types: dict,
            error_codes_map: dict
        ):
        self.notary_pubkey = notary_pubkey
        self.payment_type = payment_type
        self.circuit_type = circuit_type
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

        # Write notary key to local
        write_notary_pubkey_to_local(self.notary_pubkey, self.payment_type, self.circuit_type, str(nonce))

        # Verify the notaries signature on encoded data using the rust verifier
        print('Running verify process')
        result = self.run_verify_process(str(nonce))

        # Exit early if error is found
        if result.stderr != "":
            return "", "", result.stderr

        # Read the decoded session data output by the rust verifier
        print('Reading outputs')
        send_data, recv_data = read_tlsn_verify_output_from_local(self.payment_type, self.circuit_type, str(nonce))

        return send_data, recv_data, ""

    def run_verify_process(self, nonce):
        notary_pubkey_path = get_notary_pubkey_path(self.payment_type, self.circuit_type, nonce)
        tlsn_proof_file_path = get_tlsn_proof_file_path(self.payment_type, self.circuit_type, nonce)
        send_data_file_path = get_tlsn_send_data_file_path(self.payment_type, self.circuit_type, nonce)
        recv_data_file_path = get_tlsn_recv_data_file_path(self.payment_type, self.circuit_type, nonce)

        result = subprocess.run(
            [
                f"{self.base_path}/tlsn-verifier/target/release/tlsn-verifier",
                notary_pubkey_path,
                tlsn_proof_file_path,
                send_data_file_path,
                recv_data_file_path
            ],
            capture_output=True,
            text=True
        )
        print('Result', result.stdout)
        return result
    
    def sign_and_serialize_values(self, public_values, target_types):
        signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values, target_types)
        serialized_values = [str(v) for v in public_values]

        return signature, serialized_values


