import pytest
import os
from src.chase_zelle.api import core_verify_proof
from dotenv import load_dotenv
from fastapi.exceptions import HTTPException

# Specify the path to your .env file
# Add custom path
dotenv_path = 'src/chase_zelle/.env'
load_dotenv(dotenv_path)

# Override verifier private key to hardhat
os.environ['VERIFIER_PRIVATE_KEY'] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@pytest.mark.parametrize("proof_data, expected_output", [
    ({
        "proof": open_file("./src/chase_zelle/tests/proofs/chase_zelle_registration_1.json"),  
        "payment_type": "chase_zelle",
        "circuit_type": "registration_chase_zelle_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0x61cb0ff2845d63b785df595926a6eca440c9f4a0fa5dbf0a97e7310184c0ccf35a96d805acf3607e8cf44caaf07058e8d427fe8b753ba5049519affc418340011b",
        "public_values": [
            "GET https://secure.chase.com/svc/rr/payments/secure/gateway/quick-pay/customer/profile/digital-social-aliases/v1/social-aliases-profiles",
            "secure.chase.com",
            "76964753624536974342651895214001615442783418692201682262093777610547921264820"
        ]
    }),
    ({
        "proof": open_file("./src/chase_zelle/tests/proofs/chase_zelle_transfer_amount_1.json"),  
        "payment_type": "chase_zelle",
        "circuit_type": "transfer_amount",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0xf7f5b55a870c8f0c768e83c26cf20df9731962e01a743bdc4b900fb9a77240de5acb5c4c8cedbaffc65145d773ffd50abcc771c69e9ca4d31aa3701d12fa0b3b1b",
        "public_values": [
            "POST https://secure.chase.com/svc/rr/payments/secure/v1/quickpay/payment/activity/list",
            "secure.chase.com",
            "10",
            "Test",
            "20316293596",
            "2109098755843864455034980037347310810989244226703714011137935097150268285982"
        ]
    }),
    ({
        "proof": open_file("./src/chase_zelle/tests/proofs/chase_zelle_transfer_detail_1.json"),  
        "payment_type": "chase_zelle",
        "circuit_type": "transfer_detail",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
    }, {
        "proof": "0x61fe84cd5f5328adb3e67f7a03adc03d8ca0213cca950a1a6d53676b11e5cbf45526b607c7dcaa6c9bc2f2738b7b1f9732093be048c45cba26d061aed090137a1b",
        "public_values": [
            "POST https://secure.chase.com/svc/rr/payments/secure/v1/quickpay/payment/activity/detail/list",
            "secure.chase.com",
            "ernesto@authentictfg.com",
            "COMPLETED",
            "20230524",
            "17435800047",
            "2109098755843864455034980037347310810989244226703714011137935097150268285982"
        ]
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

# TODO: Add tests for other transaction types
# @pytest.mark.parametrize("proof_data", [
#     ({
#         "proof": open_file("./src/wise/tests/proofs/registration_chase_zelle_id_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "transfer",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "transfer",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "transfer",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "transfer",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
# ])
# def test_verify_proof_invalid_values_transfer(proof_data):
#     # Construct the email data
#     proof_data = {
#         "payment_type": proof_data['payment_type'],
#         "circuit_type": proof_data['circuit_type'],
#         "proof": proof_data['proof'],
#         "intent_hash": proof_data['intent_hash']
#     }

#     with pytest.raises(HTTPException) as exc_info:
#         core_verify_proof(proof_data)

#     assert exc_info.value.status_code == 400
#     assert exc_info.value.detail == {'code': 11, 'message': 'TLSN invalid extracted values for `transfer`'}

# @pytest.mark.parametrize("proof_data", [
#     ({
#         "proof": open_file("./src/wise/tests/proofs/registration_chase_zelle_id_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_account_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_account_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_account_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     })
# ])
# def test_verify_proof_invalid_values_account_id(proof_data):
#     # Construct the email data
#     proof_data = {
#         "payment_type": proof_data['payment_type'],
#         "circuit_type": proof_data['circuit_type'],
#         "proof": proof_data['proof'],
#         "intent_hash": proof_data['intent_hash']
#     }

#     with pytest.raises(HTTPException) as exc_info:
#         core_verify_proof(proof_data)

#     assert exc_info.value.status_code == 400
#     assert exc_info.value.detail == {'code': 13, 'message': 'TLSN invalid extracted values for `mc account registration`'}

# @pytest.mark.parametrize("proof_data", [
#     ({
#         "proof": open_file("./src/wise/tests/proofs/receive_eur_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_chase_zelle_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/move_balance_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_chase_zelle_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/cancel_transfer_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_chase_zelle_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     }),
#     ({
#         "proof": open_file("./src/wise/tests/proofs/transfer_eur_1.json"),  
#         "payment_type": "wise",
#         "circuit_type": "registration_chase_zelle_id",
#         "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
#     })
# ])
# def test_verify_proof_invalid_values_profile_id(proof_data):
#     # Construct the email data
#     proof_data = {
#         "payment_type": proof_data['payment_type'],
#         "circuit_type": proof_data['circuit_type'],
#         "proof": proof_data['proof'],
#         "intent_hash": proof_data['intent_hash']
#     }

#     with pytest.raises(HTTPException) as exc_info:
#         core_verify_proof(proof_data)

#     assert exc_info.value.status_code == 400
#     assert exc_info.value.detail == {'code': 12, 'message': 'TLSN invalid extracted values for `profile registration`'}