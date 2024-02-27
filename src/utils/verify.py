import json


tlsn_verify_send_data_path = "/root/prover-api/tlsn_verify_outputs/send_data_[payment_type]_[circuit_type]_[nonce].txt"
tlsn_verify_recv_data_path = "/root/prover-api/tlsn_verify_outputs/recv_data_[payment_type]_[circuit_type]_[nonce].txt"
tlsn_proof_file_path = "/root/prover-api/proofs/tlsn_proof_[payment_type]_[circuit_type]_[nonce].json"

def get_tlsn_send_data_file_path(payment_type, circuit_type, nonce):
    return tlsn_verify_send_data_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)

def get_tlsn_recv_data_file_path(payment_type, circuit_type, nonce):
    return tlsn_verify_recv_data_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)

def get_tlsn_proof_file_path(payment_type, circuit_type, nonce):
    return tlsn_proof_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)

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



def extract_values_from_response(input_blob, keys):
    # Split the input blob into lines
    lines = input_blob.split('\n')

    # Find the empty line separating headers from the body, then join the body parts
    json_body = '\n'.join(lines[lines.index('')+1:-1])

    # Parse the JSON body
    data = json.loads(json_body)

    # Extract the values for the specified keys
    values = [data[key] for key in keys if key in data]

    return values

