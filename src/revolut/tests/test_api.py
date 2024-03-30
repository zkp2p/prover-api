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
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0x9baec59a17fd711144d6715cfdf160ff89badc2afb0d7c0ea04820c700e12cb42caacbaa444ac53f81818bef537f907b14c614758839d3302c96191266fce6971b",
        "public_values": ["GET https://app.revolut.com/api/retail/user/current", "app.revolut.com", "21441300878620834626555326528464320548303703202526115662730864900894611908769"]
    }),
    ({
        "proof": open_file("./src/revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0x1a6db4989f793387da4045ea28c33cfa4e1cdc68f32637ff221f8c1dd785d4d559803367c00264de10b337f5c38db58cfb447e305ae5ec48a3ec3cd35943a0711b",
        "public_values": ["GET https://app.revolut.com/api/retail/transaction/65fd0142-7155-a0b7-8136-86e1fcc5455e", "app.revolut.com", "65fd0142-7155-a0b7-8136-86e1fcc5455e", "alexgx7gy", "-100", "EUR", "COMPLETED", "1711079746280", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    })
])
def test_verify_proof(proof_data, expected_output):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash']
    }

    result = core_verify_proof(proof_data)
    print (result)
    assert result == expected_output

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/revolut/tests/proofs/revtag_registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    })
])
def test_verify_proof_invalid_values_transfer(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash']
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
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    })
])
def test_verify_proof_invalid_values_revtag(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 12, 'message': 'TLSN invalid extracted values for `profile registration`'}
