import pytest
import os
from src.revolut.api import core_verify_proof
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# Specify the path to your .env file
# Add custom path
dotenv_path = 'src/revolut/.env'
load_dotenv(dotenv_path)

# Override verifier private key to hardhat
os.environ['VERIFIER_PRIVATE_KEY'] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@pytest.mark.parametrize("proof_data, expected_output", [
    ({
        "proof": open_file("./src/revolut/tests/proofs/revtag_registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration_revtag_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0x876dfdafcd4fb59d791afda6cb536fb9d22560318f83b94c7f45b1c0a7e7bf6304e50778b1068140df9fb1b5333ffd6d76fc6639e23b961e3416722f26103c721b",
        "public_values": ["GET https://app.revolut.com/api/retail/user/current", "app.revolut.com", "21441300878620834626555326528464320548303703202526115662730864900894611908769", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"]
    }),
    ({
        "proof": open_file("./src/revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0x1a6db4989f793387da4045ea28c33cfa4e1cdc68f32637ff221f8c1dd785d4d559803367c00264de10b337f5c38db58cfb447e305ae5ec48a3ec3cd35943a0711b",
        "public_values": ["GET https://app.revolut.com/api/retail/transaction/65fd0142-7155-a0b7-8136-86e1fcc5455e", "app.revolut.com", "65fd0142-7155-a0b7-8136-86e1fcc5455e", "alexgx7gy", "-100", "EUR", "COMPLETED", "1711079746280", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
    # NOTE: Receiving a transfer can also be verified correctly
    ({
        "proof": open_file("./src/revolut/tests/proofs/receive_usd_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    },{
        "proof": "0xf5eafc35635be28c551174ef56fbd69b375268bb7189d20c6e2c7d9823ddb310362c8728f78ddc14ea8482a1152c5da0c4d6792fb08ce4a7cca2d68c67d3fb6d1b",
        "public_values": ["GET https://app.revolut.com/api/retail/transaction/656a0b92-2554-a83e-962c-25a85edad060", "app.revolut.com", "656a0b92-2554-a83e-962c-25a85edad060", "alexgx7gy", "100", "USD", "COMPLETED", "1701448594254", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
    # NOTE: Transfering USD with note containing " and comma
    ({
        "proof": open_file("./src/revolut/tests/proofs/transfer_usd_with_note.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    },{
        "proof": "0x522f5f1cb740c53f11bf9ecf3b233ff66e43c86fa91a3f041e0ffc83b2c994472fe1f0d56ae43286eebd5fd7c667f003b551d5953c87dd003e76e332554092541b",
        "public_values": ["GET https://app.revolut.com/api/retail/transaction/660e6386-0a63-a388-80be-32d1f7672787", "app.revolut.com", "660e6386-0a63-a388-80be-32d1f7672787", "alexgx7gy", "-100", "USD", "COMPLETED", "1712219014734", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
])
def test_verify_proof(proof_data, expected_output):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address']
    }

    result = core_verify_proof(proof_data)
    print (result)
    assert result == expected_output

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/revolut/tests/proofs/revtag_registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    })
])
def test_verify_proof_invalid_values_transfer(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 11, 'message': 'TLSN invalid extracted values for `transfer`'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration_revtag_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    })
])
def test_verify_proof_invalid_values_revtag(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 12, 'message': 'TLSN invalid extracted values for `profile registration`'}