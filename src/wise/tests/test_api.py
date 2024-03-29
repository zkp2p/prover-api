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
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0xba03085b486a2f7bab46cef658ea930b2be69368a3f1d547d0afc99ef382cda0384e6e80a15a832c7416dc5882e9b5e05c16c6f33885a4c5794f1e1a058605831b",
        "public_values": ["POST https://wise.com/gateway/v1/payments", "wise.com", "41213881", "61158579531006309039872672420732308054473459091416465738091051601559791768344"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0x8fedde36a43e95dc6eedc10bc90dca4c8e7eebf43b7db19b62fc8bf3b043b5a668fda894f2f97dd981adff7130c1794f9ab780d69eef903f128d6200365da9331b",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "909460084", "41213881", "403384647", "1.0", "EUR", "OUTGOING_PAYMENT_SENT", "1703270934000", "2109098755843864455034980037347310810989244226703714011137935097150268285982"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0xf7f5982ae351d80e6be4029899d152a43ad554380bd4aa9a335316f11757003423209e545af86c2835ebcb4e6b5ff60748a49e3bc73129772f04f633c2fe989c1b",
        "public_values": ["GET https://wise.com/gateway/v3/profiles/41213881/transfers", "wise.com", "41213881", "402863684"]
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"), # NOTE: we allow a cancel transfer proof to pass
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
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
        "intent_hash": proof_data['intent_hash']
    }

    result = core_verify_proof(proof_data)
    print (result)
    assert result == expected_output

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/registration_profile_id_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
        "payment_type": "wise",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
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
        "proof": open_file("./src/wise/tests/proofs/registration_profile_id_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_account_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    })
])
def test_verify_proof_invalid_values_account_id(proof_data):
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
    assert exc_info.value.detail == {'code': 13, 'message': 'TLSN invalid extracted values for `mc account registration`'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }),
    ({
        "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    })
])
def test_verify_proof_invalid_values_profile_id(proof_data):
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