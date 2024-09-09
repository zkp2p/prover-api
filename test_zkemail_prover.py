
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv('./.env')

TEST_PAYMENT_TYPE = os.getenv("TEST_PAYMENT_TYPE")
TEST_CIRCUIT_TYPE = os.getenv("TEST_CIRCUIT_TYPE")
TEST_EMAIL_PATH = os.getenv("TEST_EMAIL_PATH")
MODAL_ENDPOINT = os.getenv("MODAL_ENDPOINT")

TEST_PAYMENT_TYPE = "namecheap"
TEST_CIRCUIT_TYPE = "push"
TEST_EMAIL_PATH = "./received_eml/namecheap_email.eml"
MODAL_ENDPOINT = "https://zkp2p--zkp2p-modal-namecheap-staging-0-2-6-genproof-email.modal.run"


if __name__ == "__main__":
    
    # Read an email file
    with open(TEST_EMAIL_PATH, 'r') as file:
        email = file.read()

    # Construct the email data
    email_data = {
        "payment_type": TEST_PAYMENT_TYPE,
        "circuit_type": TEST_CIRCUIT_TYPE,
        "email": email,
        "intent_hash": "12345"
    }
    print(
        "Payment Type: ", email_data['payment_type'], 
        "Circuit Type: ", email_data['circuit_type'],
        "Email path: ", TEST_EMAIL_PATH,
        "Modal endpoint: ", MODAL_ENDPOINT
    )


    start = time.time()
    response = requests.post(MODAL_ENDPOINT, json=email_data)
    end = time.time()
    print("Time taken: ", end - start)
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)