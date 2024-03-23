from utils.helpers import sha256_hash
from utils.file_utils import write_tlsn_proof_to_local, read_tlsn_verify_output_from_local
from utils.file_utils import get_tlsn_proof_file_path, get_tlsn_recv_data_file_path, get_tlsn_send_data_file_path

# Verifies the notaries signature on the encoded session data, decodes session data and extracts the 
# payment details from it. Outputs a signature proof and public signals.
def verify_tlsn_proof(proof_data):
    proof_raw_data = proof_data["proof"]
    payment_type = proof_data["payment_type"]
    circuit_type = proof_data["circuit_type"]
    
    nonce = int(sha256_hash(proof_raw_data), 16)

    # Write file to local
    write_tlsn_proof_to_local(proof_raw_data, payment_type, circuit_type, str(nonce))

    # Verify the notaries signature on encoded data using the rust verifier
    print('Running verify process')
    run_verify_process(payment_type, circuit_type, str(nonce))

    # Read the decoded session data output by the rust verifier
    print('Reading outputs')
    send_data, recv_data = read_tlsn_verify_output_from_local(payment_type, circuit_type, str(nonce))

    return send_data, recv_data


# Call wasm binary to verify TLSN proof
def run_verify_process(payment_type:str, circuit_type:str, nonce: str):

    import subprocess

    tlsn_proof_file_path_current = get_tlsn_proof_file_path(payment_type, circuit_type, nonce)
    send_data_file_path = get_tlsn_send_data_file_path(payment_type, circuit_type, nonce)
    recv_data_file_path = get_tlsn_recv_data_file_path(payment_type, circuit_type, nonce)

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

    print('Result', result.stdout)
    return result