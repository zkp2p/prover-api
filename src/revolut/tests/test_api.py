import pytest
import os
from revolut.api import core_verify_proof
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
        "proof": open_file("./revolut/tests/proofs/registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xaa4b52f8a14c21b7a03a8ecb3897a9cde955cf1d9755bd58eea2ae27bdf77afc5629717d1128a3308fcab31066427e348a4ed4c2bb6ba388133b092da27d822e1c', 
        'public_values': ['GET https://app.revolut.com/api/retail/user/current', 'app.revolut.com', '21441300878620834626555326528464320548303703202526115662730864900894611908769', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
    ({
        "proof": open_file("./revolut/tests/proofs/registration_with_termsVersion.json"),
        "payment_type": "revolut",
        "circuit_type": "registration",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0x5fe234ddea3bcdadf436c64497cac231c90aac847e67f7e6e7147eacecd125a3585d9a71caf6bbbe312de0c1b4d486ff1cde037344a1af4ec80ade6352774c3a1c', 
        'public_values': ['GET https://app.revolut.com/api/retail/user/current', 'app.revolut.com', '76999194733354397871627298999127398328850387878548124539575540187178857311010', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xc5828af173133edd0cc5db74e2f5f9782eab38f87ffa3f13b055315c4b68ec3d3ba9e57ac57154e71e6f439409a9d4b0382cbfe84fb06ff2d378087fc8e4762b1c', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/663cb3e2-5ca1-a96a-8d32-d61ad2700402', 'app.revolut.com', '663cb3e2-5ca1-a96a-8d32-d61ad2700402', 'alexgx7gy', '-113', 'EUR', 'COMPLETED', '1715254242718', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
    # NOTE: Transfering USD with note containing " and comma
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_usd_with_note.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xe6cc00959e38241de75c634d691b45f8649297df27f73bbfe863733c970157a272474d144e7327f41c4962e43f45335ef9e13a5b267c6c724807fc11c49783871c', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/660e6386-0a63-a388-80be-32d1f7672787', 'app.revolut.com', '660e6386-0a63-a388-80be-32d1f7672787', 'alexgx7gy', '-100', 'USD', 'COMPLETED', '1712219014734', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
    # NOTE: Transfering USD with formatted quotes
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_usd_with_note_2.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0x0cedd0df5132aa5253784ee278c3ead5734c5576489624842067f4145ad0449348fcd48cea52e7c14e98b08787dcec3bacd2b428144c4f64b1cbae1f7baeafc01c', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/66292307-f9c8-afbf-aac5-9d432cd7da24', 'app.revolut.com', '66292307-f9c8-afbf-aac5-9d432cd7da24', 'alexgx7gy', '-100', 'USD', 'COMPLETED', '1713971975510', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
    # NOTE: Updated revtag, but should still keep same code
    ({
        "proof": open_file("./revolut/tests/proofs/registration_username_change.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xc1b2b6fc8a72c246e499e2efa084d0e275bc6d85888ce048a284c3a1da36b101730c1d05c6a06915335735e4889947b8a5d958fd4a624b30366593833bf305281c', 
        'public_values': ['GET https://app.revolut.com/api/retail/user/current', 'app.revolut.com', '21441300878620834626555326528464320548303703202526115662730864900894611908769', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', '112089371709673661805969872300503488524525726634528779705618943730435390735319']
    }),
    # NOTE: Test for when balance is 17 and matches the first 2 UNIX timestamp characters (Vivek's bug)
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_eur_17_balance.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xb92b50d8c77b6bb60e584e63d918b914423afd81ce3256427c7134d221710bec57647fe63f44469cb8fbe14534e3e498bee03c36d48216c7e0f3dd6fa9e072a11b', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/6645bf63-fb9a-a261-93cf-312d1886b92a', 'app.revolut.com', '6645bf63-fb9a-a261-93cf-312d1886b92a', 'alexgx7gy', '-199', 'EUR', 'COMPLETED', '1715847011200', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '113116629262703480258914951290401242193028831780154554089583031844538369800942']
    }),
])
def test_verify_proof(proof_data, expected_output):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    result = core_verify_proof(proof_data)
    print (result)
    assert result == expected_output

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./revolut/tests/proofs/registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }),
    ({
        "proof": open_file("./revolut/tests/proofs/receive_usd_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }),
])
def test_verify_proof_invalid_values_transfer(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 11, 'message': 'TLSN invalid extracted values for `transfer`'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "registration",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    })
])
def test_verify_proof_invalid_values_revtag(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 12, 'message': 'TLSN invalid extracted values for `profile registration`'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./revolut/tests/proofs/registration_1.json"),  
        "payment_type": "wise",
        "circuit_type": "registration",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }),
])
def test_verify_proof_invalid_payment_type(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 1, 'message': 'Invalid payment type'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./revolut/tests/proofs/registration_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "invalid_transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }),
])
def test_verify_proof_invalid_circuit_type(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 2, 'message': 'Invalid circuit type. Circuit type should be send or registration'}

@pytest.mark.parametrize("proof_data", [
    ({
        "proof": open_file("./revolut/tests/proofs/invalid_proof.json"),
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEhXZItBvE1R/gcSGKGMrl7cPpybNy\niTJ5B4ejf6chkzVKsjYnljqiD/4eEIl69+Y4QZFb57yvQ10Dq2ntdGMxXQ==\n-----END PUBLIC KEY-----"
    }),
])
def test_verify_proof_invalid_proof(proof_data):
    # Construct the email data
    proof_data = {
        "payment_type": proof_data['payment_type'],
        "circuit_type": proof_data['circuit_type'],
        "proof": proof_data['proof'],
        "intent_hash": proof_data['intent_hash'],
        "user_address": proof_data['user_address'],
        "notary_pubkey": proof_data['notary_pubkey']
    }

    with pytest.raises(HTTPException) as exc_info:
        core_verify_proof(proof_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {'code': 10, 'message': 'TLSN proof verification failed'}