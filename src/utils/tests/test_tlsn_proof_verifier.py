import pytest
import os
from src.utils.tlsn_proof_verifier import TLSNProofVerifier
from dotenv import load_dotenv

# Specify the path to your .env file
# Add custom path
dotenv_path = "src/wise/.env"
load_dotenv(dotenv_path)

# Override verifier private key to hardhat
os.environ['VERIFIER_PRIVATE_KEY'] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

@pytest.mark.parametrize("inputs, expected_output", [
    # When both regexes pass
    ({
        "payment_type": "wise",
        "circuit_type": "transfer",
        "regex_patterns_map": {
            "transfer": [
                r'"id":(\d+)',
                r'"targetCurrency":"([A-Z]{3})"'
            ]
        },
        "regex_target_types": {
            "transfer": ["string", "string"]
        },
        "error_codes_map": {
            "transfer": 11
        },
        "send_data": 'AAAAAA,"targetCurrency":"EUR",XXXXXX',
        "recv_data": 'AAAAAA,"id":41213881,XXXXXX'  
    }, {
        "public_values": ["41213881", "EUR"],
        "valid": True,
        "error_code": ""
    }),
    # When one of the regexes doesn't pass
    ({
        "payment_type": "wise",
        "circuit_type": "transfer",
        "regex_patterns_map": {
            "transfer": [
                r'"id":(\d+)',
                r'"targetCurrency":"([A-Z]{3})"'
            ]
        },
        "regex_target_types": {
            "transfer": ["string", "string"]
        },
        "error_codes_map": {
            "transfer": 11
        },
        "send_data": 'AAAAAA,"sourceCurrency":"EUR",XXXXXX',
        "recv_data": 'AAAAAA,"id":41213881,XXXXXX'  
    }, {
        "public_values": [],
        "valid": False,
        "error_code": 11
    }),
    # When 2 matches
    ({
        "payment_type": "wise",
        "circuit_type": "transfer",
        "regex_patterns_map": {
            "transfer": [
                r'"id":(\d+)',
                r'"targetCurrency":"([A-Z]{3})"'
            ]
        },
        "regex_target_types": {
            "transfer": ["string", "string"]
        },
        "error_codes_map": {
            "transfer": 11
        },
        "send_data": 'AAAAAA,"targetCurrency":"EUR",XXXXXX',
        "recv_data": 'AAAAAA,"id":41213881,XXXXXXAAAAAA,"id":41213881,XXXXXX'  
    }, {
        "public_values": ["41213881", "EUR"],
        "valid": True,
        "error_code": ""
    })
])
def test_verify_extracted_regexes(inputs, expected_output):
    public_values, valid, error_code = TLSNProofVerifier(
        payment_type=inputs["payment_type"],
        circuit_type=inputs["circuit_type"],
        regex_patterns_map=inputs["regex_patterns_map"],
        regex_target_types=inputs["regex_target_types"],
        error_codes_map=inputs["error_codes_map"]
    ).verify_extracted_regexes(inputs["send_data"], inputs["recv_data"])

    assert public_values == expected_output["public_values"]
    assert valid == expected_output["valid"]
    assert error_code == expected_output["error_code"]
