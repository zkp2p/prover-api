
import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv('./.env')

TEST_PAYMENT_TYPE = "revolut"
TEST_CIRCUIT_TYPE = "transfer"
NOTARY_PUBKEY_PATH = "./certs/zkp2p_notary.pub"
TEST_PROOF_PATH = "./proofs/revolut/transfer_proof_new_notary_key.json"
MODAL_ENDPOINT = "https://zkp2p--zkp2p-revolut-verifier-0-2-5-verify-proof-dev.modal.run"


if __name__ == "__main__":
    
    # Read the proof file
    with open(TEST_PROOF_PATH, 'r') as file:
        proof = file.read()

    # Read the notary pubkey file
    with open(NOTARY_PUBKEY_PATH, 'r') as file:
        notary_pubkey = file.read()

    # Construct the email data
    proof_data = {
        "payment_type": TEST_PAYMENT_TYPE,
        "circuit_type": TEST_CIRCUIT_TYPE,
        "notary_pubkey": notary_pubkey,
        "proof": proof,
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }
    print(proof_data)
    # print(
    #     "Payment Type: ", proof_data['payment_type'], 
    #     "Circuit Type: ", proof_data['circuit_type']
    # )


    start = time.time()
    response = requests.post(MODAL_ENDPOINT, json=proof_data)
    end = time.time()
    print("Time taken: ", end - start)
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)