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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xc1b2b6fc8a72c246e499e2efa084d0e275bc6d85888ce048a284c3a1da36b101730c1d05c6a06915335735e4889947b8a5d958fd4a624b30366593833bf305281c', 
        'public_values': ['GET https://app.revolut.com/api/retail/user/current', 'app.revolut.com', '21441300878620834626555326528464320548303703202526115662730864900894611908769', '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266', '112089371709673661805969872300503488524525726634528779705618943730435390735319']}
    ),
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_eur_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0x4639170533d3613c0b30be64b95dc4a6db4c12b38a0c43162a02205d60bbc55a060d050b8bf1246ee5110f63b68a54ef7a13514644bd1997edbd476e39535ba71b', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/65fd0142-7155-a0b7-8136-86e1fcc5455e', 'app.revolut.com', '65fd0142-7155-a0b7-8136-86e1fcc5455e', 'alexgx7gy', '-100', 'EUR', 'COMPLETED', '1711079746280', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '112089371709673661805969872300503488524525726634528779705618943730435390735319']
    }),
    # NOTE: Transfering USD with note containing " and comma
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_usd_with_note.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0xda382f15326757951facc15ed60cb016eb14439e05c3ff1ecd260475a0df9f3b536c00a081505c5c5fa6b35e33131243844b389f7dc88de188d9c132988d3f851c', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/660e6386-0a63-a388-80be-32d1f7672787', 'app.revolut.com', '660e6386-0a63-a388-80be-32d1f7672787', 'alexgx7gy', '-100', 'USD', 'COMPLETED', '1712219014734', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '112089371709673661805969872300503488524525726634528779705618943730435390735319']
    }),
    # NOTE: Transfering USD with formatted quotes
    ({
        "proof": open_file("./revolut/tests/proofs/transfer_usd_with_note_2.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }, {
        'proof': '0x5cdbec48024ccb348694e0364a34aae08113a597182a4ceda1b020a91020cf721a010b93d234a1b511541765670f61167f171482ccdc330bace8c04760a9ea511c', 
        'public_values': ['GET https://app.revolut.com/api/retail/transaction/66292307-f9c8-afbf-aac5-9d432cd7da24', 'app.revolut.com', '66292307-f9c8-afbf-aac5-9d432cd7da24', 'alexgx7gy', '-100', 'USD', 'COMPLETED', '1713971975510', '2109098755843864455034980037347310810989244226703714011137935097150268285982', '112089371709673661805969872300503488524525726634528779705618943730435390735319']
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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
    }),
    ({
        "proof": open_file("./revolut/tests/proofs/receive_usd_1.json"),  
        "payment_type": "revolut",
        "circuit_type": "transfer",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982",
        "user_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
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
        "notary_pubkey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBv36FI4ZFszJa0DQFJ3wWCXvVLFr\ncRzMG5kaTeHGoSzDu6cFqx3uEWYpFGo6C0EOUgf+mEgbktLrXocv5yHzKg==\n-----END PUBLIC KEY-----"
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