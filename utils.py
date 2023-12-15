import dkim
from dns import resolver
import re
import hashlib
import requests
import os
from dotenv import load_dotenv

def fetch_domain_key(domain, selector='default'):
    try:
        answers = resolver.query(f"{selector}._domainkey.{domain}", 'TXT')
        return answers[0].strings[0].decode('utf-8')
    except Exception as e:
        print(f"Error fetching domain key: {e}")
        return None
 
def validate_dkim(email_raw):
    try:
        d = dkim.DKIM(email_raw.encode('utf-8'))
        valid = d.verify()
        return valid
    except Exception as e:
        print(f"Error during DKIM validation: {e}")
        return False

def sha256_hash(text):
    m = hashlib.sha256()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

def match_and_sub(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            log_text = text.replace(match.group(1), '').replace(match.group(2), '')
            return log_text.strip()
    return ""


def upload_file_to_slack(channels, token, initial_comment, file_content):
    """Uploads a file to Slack."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "channels": channels,
        "initial_comment": initial_comment,
    }
    response = requests.post(
        "https://slack.com/api/files.upload", 
        headers=headers, 
        params=payload, 
        files=file_content
    )
    return response

# --------- PROOFGEN HELPER FUNCTIONS ------------

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


def prove_email(payment_type:str, circuit_type:str, nonce: str, intent_hash: str, c_witness_gen: str):
    print('Running prove email')
    
    import subprocess 

    # Run the circom proofgen script
    result = subprocess.run(
        [
            '/root/prover-api/circom_proofgen.sh', 
            payment_type, 
            circuit_type, 
            nonce, intent_hash, 
            c_witness_gen
        ],
        capture_output=True, 
        text=True
    )
    print(result.stdout)
    
    # Read the proof and public values 
    proof, public_values = read_proof_from_local(payment_type, circuit_type, nonce)
    return proof, public_values


# ----------- ENV VARIABLES ------------ (Todo: Clean this)

def read_env_credentials():
    env_example_path = "./.env.example"
    env_credentials = {}
    if os.path.isfile(env_example_path):
        def get_variable_names_from_env_file(file_path=env_example_path):
            variable_names = []
            with open(file_path) as file:
                for line in file:
                    # Ignore comments and empty lines
                    if line.startswith('#') or line.strip() == '':
                        continue
                    # Extract variable name (part before the '=' character)
                    variable_name = line.split('=')[0].strip()
                    variable_names.append(variable_name)
            return variable_names

        # Load additional environment variables from the .env file
        additional_vars = get_variable_names_from_env_file()
        load_dotenv()  # Load environment variables from .env file
        for var_name in additional_vars:
            # If it doesnt start with local
            if not var_name.startswith("LOCAL_"):
                var_value = os.getenv(var_name)
                if var_value is not None:
                    # TODO: Make this cleaner; remove all uses of a non local/modal path env var
                    env_credentials[var_name] = var_value
                    var_name = var_name.replace("MODAL_", "")
                    env_credentials[var_name] = var_value
    return env_credentials
    

# ----------- PREPROCESSING EMAILS ------------

def replace_message_id_with_x_google_original_message_id(email_raw_content):
    message_id_label = "Message-ID: <"
    x_google_message_id_label = "X-Google-Original-Message-ID: "

    message_id_start = email_raw_content.find(message_id_label) + len(message_id_label)
    message_id_end = email_raw_content.find(">", message_id_start)
    message_id = email_raw_content[message_id_start: message_id_end]
    # print("message_id", message_id)

    # Replace "<message-id>" with "x-message-id" if message id contains "SMTPIN_ADDED_BROKEN@mx.google.com"
    if "SMTPIN_ADDED_BROKEN@mx.google.com" not in message_id:
        return email_raw_content

    x_message_id_start = email_raw_content.find(x_google_message_id_label) + len(x_google_message_id_label)
    x_message_id_end = email_raw_content.find(".com", x_message_id_start) + len(".com")
    x_message_id = email_raw_content[x_message_id_start: x_message_id_end]
    # print("x_message_id", x_message_id)

    # Replace "<message-id>" with "x-message-id"
    return email_raw_content.replace("<" + message_id + ">", x_message_id)

if __name__ == "__main__":
    
    # Fetch domain key
    email_raw = open("./received_eml/hdfc_send_sachin_nov_4.eml", "r").read()

    # replace and print
    email_raw = replace_message_id_with_x_google_original_message_id(email_raw)
    print(email_raw)