import modal
import re
import boto3
import subprocess
import os
from dotenv import load_dotenv
from enum import Enum
from fastapi import FastAPI, HTTPException, status
from typing import Dict


load_dotenv()       # Load environment variables from .env file
bucket_name = "relayer-emails-zkp2p"  # Replace with your S3 bucket name
object_key_template = "emls/venmo_[email_type]_[nonce].txt"  # Replace with the desired object key (name) in S3
s3_url = "https://" + bucket_name + ".s3.amazonaws.com/" + object_key_template

# Paths
incoming_eml_file_path = "/root/prover-api/received_eml/venmo_[email_type]_[nonce].eml"
proof_file_path = "/root/prover-api/proofs/rapidsnark_proof_[email_type]_[nonce].json"
public_values_file_path = "/root/prover-api/proofs/rapidsnark_public_[email_type]_[nonce].json"


# ----------------- LOCAL ENV -----------------
# Define the paths to the AWS config and credentials files
aws_config_path = os.path.expanduser('~/.aws/config')
aws_credentials_path = os.path.expanduser('~/.aws/credentials')
aws_credentials = {}

# Check if both the config and credentials files exist
if os.path.isfile(aws_config_path) and os.path.isfile(aws_credentials_path):
    print("AWS has been configured.")
    # Read AWS credentials from the environment variables or configuration files
    session = boto3.Session()
    aws_credentials = {
        'AWS_ACCESS_KEY_ID': session.get_credentials().access_key,
        'AWS_SECRET_ACCESS_KEY': session.get_credentials().secret_key
    }
else:
    print("AWS has not been configured. Please run 'aws configure' to set up your AWS credentials.")


# --------- AWS HELPER FUNCTIONS ------------

def write_file_to_local(file_contents, email_type, nonce):
    file_path = incoming_eml_file_path.replace("[email_type]", email_type).replace("[nonce]", nonce)
    with open(file_path, 'w') as file:
        file.write(file_contents)
    return file_path


def read_proof_from_local(email_type, nonce):
    proof = ""
    public_values = ""
    proof_file_name = proof_file_path.replace("[email_type]", email_type).replace("[nonce]", nonce)
    public_values_file_name = public_values_file_path.replace("[email_type]", email_type).replace("[nonce]", nonce)

    # check if the file exists
    if not os.path.isfile(proof_file_name) or not os.path.isfile(public_values_file_name):
        print("Proof file does not exist")
        return proof, public_values

    with open(proof_file_name, 'r') as file:
        proof = file.read()
    
    with open(public_values_file_name, 'r') as file:
        public_values = file.read()
    
    return proof, public_values


def download_and_write_file(s3_url, email_type, nonce):
    # Extract the bucket name and object key from the S3 URL
    s3_url_parts = s3_url.replace("https://", "").replace("[nonce]", nonce).replace("[email_type]", email_type).split("/")
    bucket_name = s3_url_parts[0].split(".")[0]
    object_key = "/".join(s3_url_parts[1:])

    # Create an S3 client using boto3
    s3_client = boto3.client("s3")

    # Download the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_contents = response['Body'].read().decode('utf-8')

    # Write the file to the local filesystem
    write_file_to_local(file_contents, email_type, nonce)
    
    return file_contents

# Uploads file to s3 and returns the url
def upload_eml_to_s3(local_file_path, bucket_name, email_type, nonce):
    object_key = object_key_template.replace("[email_type]", email_type).replace("[nonce]", nonce)

    # Create an S3 client using boto3
    s3_client = boto3.client('s3')

    # Upload the file to S3 with private access (default)
    s3_client.upload_file(local_file_path, bucket_name, object_key, ExtraArgs={'ACL': 'private'})

    # Print a success message
    print(f"File '{local_file_path}' uploaded to {bucket_name}/{object_key} as a private object.")

    return s3_url.replace("[email_type]", email_type).replace("[nonce]", nonce)

# ----------- ENV VARIABLES ------------ (Todo: Clean this)

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

# Merge the credentials and aws_credentials dictionaries
merged_credentials = {**env_credentials, **aws_credentials}
print("merged crednetials", merged_credentials)


# ----------------- MODAL -----------------

image = modal.Image.from_registry(
    "0xsachink/zkp2p:modal", 
    add_python="3.11"
).pip_install_from_requirements("requirements.txt")
stub = modal.Stub(image=image)
stub['credentials_secret'] = modal.Secret.from_dict(merged_credentials)


@stub.function(cpu=14, memory=6000, secret=stub['credentials_secret'])
def prove_email(email_type: str, nonce: str):
    print('Running prove email')       # Todo: Remove this later.
    
    import subprocess 

    # Run the circom proofgen script
    result = subprocess.run(['/root/prover-api/circom_proofgen.sh', email_type, nonce], capture_output=True, text=True)
    print(result.stdout)        # Todo: Remove this later.
    
    # Read the proof and public values 
    proof, public_values = read_proof_from_local(email_type, nonce)
    return proof, public_values


@stub.function(cpu=14, memory=6000, secret=stub['credentials_secret'])
def pull_and_prove_email(s3_url: str, email_type: str, nonce: str):
    print('Running pull and prove email')       # Todo: Remove this later.
    
    download_and_write_file(s3_url, email_type, nonce)
    proof, public_values = prove_email(email_type, nonce)
    return proof, public_values


# ----------------- API -----------------

send_nonce = 0
receive_nonce = 0
registration_nonce = 0

@stub.function(cpu=14, memory=6000, secret=stub['credentials_secret'])
@modal.web_endpoint(method="POST")
def genproof_email(email_data: Dict):

    email_type = email_data["email_type"]
    
    # Increment nonce
    # todo: Make nonce as hash of the email
    if email_type == "send":
        global send_nonce
        send_nonce += 1
    elif email_type == "receive":
        global receive_nonce
        receive_nonce += 1
    elif email_type == "registration":
        global registration_nonce
        registration_nonce += 1
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email type")

    # Todo: Validate the email_data

    # Write file to local
    write_file_to_local(email_data["email"], email_type, str(send_nonce))

    # Prove
    proof, public_values = prove_email(email_type, str(send_nonce))

    # Uncomment to debug
    # new_env = os.environ.copy()
    # x = subprocess.run(["ls", f"/root/zk-p2p/circuits-circom/build/venmo_{email_type}"], text=True, env=new_env)
    # print(x.stdout)
    # x = subprocess.run(["ls", "/root/prover-api/received_eml/"], text=True, env=new_env)
    # print(x.stdout)
    # x = subprocess.run(["ls", "/root/prover-api/inputs/"], text=True, env=new_env)
    # print(x.stdout)
    # x = subprocess.run(["ls", "/root/prover-api/proofs/"], text=True, env=new_env)
    # print(x.stdout)


    if proof == "" or public_values == "":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Proof generation failed")

    # Construct a HTTP response
    response = {
        "proof": proof,
        "public_values": public_values
    }

    return response


# ----------------- Modal Inovke -----------------

@stub.local_entrypoint()
def run_modal():

    # Read an email file
    with open('./received_eml/test.eml', 'r') as file:
        email = file.read()

    # Construct the email data
    email_data = {
        "email_type": "send",
        "email": email
    }

    # Call the prove_email function
    response = genproof_email.remote(email_data)
    print(response)

# ---------------- Run local (inside Docker) or serve and hit the APi -----------------

TEST_EMAIL_TYPE = os.getenv("TEST_EMAIL_TYPE")
TEST_EMAIL_PATH = os.getenv("TEST_EMAIL_PATH")

TEST_LOCAL_RUN = False
TEST_ENDPOINT = True

# confirm only one test is true
if TEST_LOCAL_RUN + TEST_ENDPOINT != 1:
    raise Exception("Only one test should be true")

if __name__ == "__main__":
    
    # Read an email file
    with open(TEST_EMAIL_PATH, 'r') as file:
        email = file.read()

    # Construct the email data
    email_data = {
        "email_type": TEST_EMAIL_TYPE,
        "email": email
    }

    if TEST_LOCAL_RUN:
        # Call the prove_email function
        response = genproof_email.local(email_data)
        print(response)
    
    elif TEST_ENDPOINT:
        # call the endpoint
        import requests
        response = requests.post("https://0xsachink--api-py-genproof-email-dev.modal.run/", json=email_data)
        print(response.json())
    
    else:
        pass