from utils.helpers import sha256_hash
from utils.regex_helpers import extract_values
from utils.sign import sign_values_with_private_key
from utils.file_utils import write_tlsn_proof_to_local, read_tlsn_verify_output_from_local
from utils.file_utils import get_tlsn_proof_file_path, get_tlsn_recv_data_file_path, get_tlsn_send_data_file_path

# Verifies the notaries signature on the encoded session data, decodes session data and extracts the 
# payment details from it. Outputs a signature proof and public signals.
def verify_tlsn_proof(proof_data, send_regex_patterns, registration_regex_patterns):
    proof_raw_data = proof_data["proof"]
    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]
    intent_hash = proof_data["intent_hash"]
    
    nonce = int(sha256_hash(proof_raw_data), 16)

    # Write file to local
    write_tlsn_proof_to_local(proof_raw_data, payment_type, circuit_type, str(nonce))

    # Verify the notaries signature on encoded data using the rust verifier
    run_verify_process(payment_type, circuit_type, str(nonce))

    # Read the decoded session data output by the rust verifier
    send_data, recv_data = read_tlsn_verify_output_from_local(payment_type, circuit_type, str(nonce))

    # Extract payment details from session data
    regex_patterns = send_regex_patterns if circuit_type == "send" else registration_regex_patterns
    public_values = extract_values(
        input=send_data + recv_data,
        regex_patterns=regex_patterns
    )
    public_values.append(intent_hash)

    # Sign on payment details using verifier private key
    signature = sign_values_with_private_key('VERIFIER_PRIVATE_KEY', public_values)
    
    return signature, public_values


# Call wasm binary to verify TLSN proof
def run_verify_process(payment_type:str, circuit_type:str, nonce: str):

    import subprocess

    tlsn_proof_file_path_current = get_tlsn_proof_file_path(payment_type, circuit_type, nonce)
    send_data_file_path = get_tlsn_send_data_file_path(payment_type, circuit_type, nonce)
    recv_data_file_path = get_tlsn_recv_data_file_path(payment_type, circuit_type, nonce)

    print(send_data_file_path, 'send_data_file_path')

    result = subprocess.run(
        [
            '/root/prover-api/tlsn-verifier/target/release/tlsn-verifier',
            tlsn_proof_file_path_current,
            send_data_file_path,
            recv_data_file_path
        ],
        capture_output=True,
        text=True
    )

    print('done executin')

    print(result.stdout)
    return result