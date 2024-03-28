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
    with patch('src.wise.api.alert_helper.alert_on_slack') as mock_alert_on_slack: 
    # with patch('src.wise.api.verify_tlsn_proof') as mock_verify_tlsn_proof, \
        #  patch('src.wise.api.extract_regex_values') as mock_extract_regex_values, \
        #  patch('src.wise.api.validate_extracted_public_values') as mock_validate_extracted_public_values, \
        #  patch('src.wise.api.sign_values_with_private_key') as mock_sign_values_with_private_key, \
        #  patch('src.wise.api.alert_helper.alert_on_slack') as mock_alert_on_slack:
        # mock_verify_tlsn_proof.return_value = ("send_data", "recv_data")
        # mock_extract_regex_values.return_value = ["extracted_value1", "extracted_value2"]
        # mock_validate_extracted_public_values.return_value = (True, None)
        # mock_sign_values_with_private_key.return_value = "signature"
        yield

@pytest.mark.parametrize("proof_file, expected_output", [
    ({
        "file_path": "./src/wise/tests/proofs/tlsn_proof_wise_registration_profile_id_45303336118233766110573250619741171436958035433919655271334289679741657086812.json", 
        "payment_type": "wise",
        "circuit_type": "registration_profile_id",
        "intent_hash": "2109098755843864455034980037347310810989244226703714011137935097150268285982"
     }, {
        "proof": "signature",
        "public_values": ["extracted_value1", "extracted_value2"]
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
