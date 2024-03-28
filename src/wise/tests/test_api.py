import pytest
import json
from unittest.mock import patch, MagicMock
from src.wise.api import core_verify_proof, Error, regex_patterns_map, regex_target_types  # Update the import path as needed
from dotenv import load_dotenv

# Specify the path to your .env file
dotenv_path = 'src/wise/.env'
load_dotenv(dotenv_path)

@pytest.fixture
def mock_dependencies():
    with patch('src.wise.api.alert_helper.alert_on_slack') as mock_alert_on_slack, \
         patch('src.wise.api.sign_values_with_private_key') as mock_sign_values_with_private_key:
        # TODO: Currently a mock signature 
        mock_sign_values_with_private_key.return_value = "signature"
        yield

@pytest.mark.parametrize("proof_file, expected_output", [
    ({
        "file_path": "./src/wise/tests/proofs/registration_profile_id_1.json", 
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
     }, {
        "proof": "signature", # Mock signature
        "public_values": ["POST https://wise.com/gateway/v1/payments", "wise.com", "41213881", "61158579531006309039872672420732308054473459091416465738091051601559791768344"]
     }),
])
def test_core_verify_proof(mock_dependencies, proof_file, expected_output):
    # Read an email file
    with open(proof_file['file_path'], 'r') as file:
        proof = file.read()

    # Construct the email data
    proof_data = {
        "payment_type": proof_file['payment_type'],
        "circuit_type": proof_file['circuit_type'],
        "proof": proof,
        "intent_hash": proof_file['intent_hash']
    }

    result = core_verify_proof(proof_data)
    print (result)
    assert result == expected_output
