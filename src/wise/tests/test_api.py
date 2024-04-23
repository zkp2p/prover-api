import pytest
import os
from src.wise.api import core_verify_proof
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# Specify the path to your .env file
# Add custom path
dotenv_path = 'src/wise/.env'
load_dotenv(dotenv_path)

# Override verifier private key to hardhat
os.environ['VERIFIER_PRIVATE_KEY'] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@pytest.mark.parametrize("proof_data, expected_output", [
    ({
        "proof": open_file("./src/wise/tests/proofs/registration_profile_id_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0xe8d9937381ea1a4e4079d1007edc3d63fbeeb62b5759c9259f1c11b671ef8b7014fb621bea79abfe22aa3d29a77d2601adb25b55890c2f3e1f9f436870d549b61b",
        "public_values": ["POST https://wise.com/gateway/v1/payments", "wise.com", "41213881", "61158579531006309039872672420732308054473459091416465738091051601559791768344","0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0x8fedde36a43e95dc6eedc10bc90dca4c8e7eebf43b7db19b62fc8bf3b043b5a668fda894f2f97dd981adff7130c1794f9ab780d69eef903f128d6200365da9331b",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "909460084", "41213881", "403384647", "1.0", "EUR", "OUTGOING_PAYMENT_SENT", "1703270934000", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_sgd_note.json"),  # NOTE: special characters are not allowed in the custom note to prevent injection attacks
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0xa97022e62b9dee81915f57041c0fefd2566698fddc5656fe21e7fd51edd625786519741756e24820807a2c566c03bbe0d2684f86a2248722f3f4d6068d9ec8501c",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "1018659478", "41213881", "403384647", "0.1", "SGD", "OUTGOING_PAYMENT_SENT", "1711957984000", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0xf7f5982ae351d80e6be4029899d152a43ad554380bd4aa9a335316f11757003423209e545af86c2835ebcb4e6b5ff60748a49e3bc73129772f04f633c2fe989c1b",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "41213881", "402863684"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"), # NOTE: we allow a cancel transfer proof to pass
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }, {
        "proof": "0xf7f5982ae351d80e6be4029899d152a43ad554380bd4aa9a335316f11757003423209e545af86c2835ebcb4e6b5ff60748a49e3bc73129772f04f633c2fe989c1b",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "41213881", "402863684"]
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
        "proof": open_file("./src/wise/tests/proofs/registration_profile_id_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
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
        "proof": open_file("./src/wise/tests/proofs/registration_profile_id_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    })
])
def test_verify_proof_invalid_values_account_id(proof_data):
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
    assert exc_info.value.detail == {'code': 13, 'message': 'TLSN invalid extracted values for `mc account registration`'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    })
])
def test_verify_proof_invalid_values_profile_id(proof_data):
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

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
])
def test_verify_proof_invalid_payment_type(proof_data):
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
    assert exc_info.value.detail == {'code': 1, 'message': 'Invalid payment type'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "invalid_transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
])
def test_verify_proof_invalid_circuit_type(proof_data):
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
    assert exc_info.value.detail == {'code': 2, 'message': 'Invalid circuit type. Circuit type should be send or registration'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/invalid_proof.json"),
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    }),
])
def test_verify_proof_invalid_proof(proof_data):
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
    assert exc_info.value.detail == {'code': 10, 'message': 'TLSN proof verification failed'}