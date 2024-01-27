import os

incoming_eml_file_path = "/root/prover-api/received_eml/[payment_type]_[circuit_type]_[nonce].eml"
proof_file_path = "/root/prover-api/proofs/rapidsnark_proof_[payment_type]_[circuit_type]_[nonce].json"
public_values_file_path = "/root/prover-api/proofs/rapidsnark_public_[payment_type]_[circuit_type]_[nonce].json"


def write_file_to_local(file_contents, payment_type, circuit_type, nonce):
    file_path = incoming_eml_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)
    with open(file_path, 'w') as file:
        file.write(file_contents)
    return file_path


def read_proof_from_local(payment_type, circuit_type, nonce):
    proof = ""
    public_values = ""
    proof_file_name = proof_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)
    public_values_file_name = public_values_file_path\
        .replace("[payment_type]", payment_type)\
        .replace("[circuit_type]", circuit_type)\
        .replace("[nonce]", nonce)

    # check if the file exists
    if not os.path.isfile(proof_file_name) or not os.path.isfile(public_values_file_name):
        print("Proof file does not exist")
        return proof, public_values

    with open(proof_file_name, 'r') as file:
        proof = file.read()
    
    with open(public_values_file_name, 'r') as file:
        public_values = file.read()
    
    return proof, public_values
