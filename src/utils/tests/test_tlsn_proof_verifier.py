import pytest
import os
from src.utils.tlsn_proof_verifier import TLSNProofVerifier
from dotenv import load_dotenv

# Specify the path to your .env file
# Add custom path
dotenv_path = "src/utils/tests/.env"
load_dotenv(dotenv_path)

# Override verifier private key to hardhat
os.environ['VERIFIER_PRIVATE_KEY'] = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

def open_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

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
def test_extract_regexes(inputs, expected_output):
    public_values, valid, error_code = TLSNProofVerifier(
        payment_type=inputs["payment_type"],
        circuit_type=inputs["circuit_type"],
        regex_patterns_map=inputs["regex_patterns_map"],
        regex_target_types=inputs["regex_target_types"],
        error_codes_map=inputs["error_codes_map"]
    ).extract_regexes(inputs["send_data"], inputs["recv_data"])

    assert public_values == expected_output["public_values"]
    assert valid == expected_output["valid"]
    assert error_code == expected_output["error_code"]

@pytest.mark.parametrize("inputs, expected_output", [
    # Sample notary proof
    ({
        "payment_type": "swapi",
        "circuit_type": "people",
        "proof_raw_data": open_file("./src/utils/tests/proofs/swapi.json")
    }, {
        "send_data": "GET https://swapi.dev/api/people/1/ HTTP/1.1\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXX\nconnection: close\nXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXX\nhost: swapi.dev\nXXXXXXXXXXXXXXXXXXXXX\naccept-encoding: identity\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n",
        "recv_data": 'HTTP/1.1 200 OK\nServer: nginx/1.16.1\nDate: Mon, 01 Apr 2024 05:38:36 GMT\nContent-Type: application/json\nTransfer-Encoding: chunked\nConnection: close\nVary: Accept, Cookie\nX-Frame-Options: SAMEORIGIN\nETag: "ee398610435c328f4d0a4e1b0d2f7bbc"\nAllow: GET, HEAD, OPTIONS\nStrict-Transport-Security: max-age=15768000\n\n287\n{"name":"Luke Skywalker","height":"172","mass":"77","hair_color":"blond","skin_color":"fair","eye_color":"blue","birth_year":"19BBY","gender":"male","homeworld":"https://swapi.dev/api/planets/1/","films":["https://swapi.dev/api/films/1/","https://swapi.dev/api/films/2/","https://swapi.dev/api/films/3/","https://swapi.dev/api/films/6/"],"species":[],"vehicles":["https://swapi.dev/api/vehicles/14/","https://swapi.dev/api/vehicles/30/"],"starships":["https://swapi.dev/api/starships/12/","https://swapi.dev/api/starships/22/"],"created":"2014-12-09T13:50:51.644000Z","edited":"2014-12-20T21:17:56.891000Z","url":"https://swapi.dev/api/people/1/"}\n0\n\n',
        "error": ""
    }),
    # Invalid proof
    ({
        "payment_type": "swapi",
        "circuit_type": "people",
        "proof_raw_data": open_file("./src/utils/tests/proofs/invalid_proof.json")
    }, {
        "send_data": "",
        "recv_data": "",
        "error": "thread \'main\' panicked at src/main.rs:50:10:\ncalled `Result::unwrap()` on an `Err` value: InvalidSignature(SignatureVerifyError(\"signature error\"))\nnote: run with `RUST_BACKTRACE=1` environment variable to display a backtrace\n"
    }),
])
def test_verify_proof(inputs, expected_output):
    send_data, recv_data, error = TLSNProofVerifier(
        payment_type=inputs["payment_type"],
        circuit_type=inputs["circuit_type"],
        regex_patterns_map={},
        regex_target_types={},
        error_codes_map={}
    ).verify_tlsn_proof(inputs["proof_raw_data"])

    assert send_data == expected_output["send_data"]
    assert recv_data == expected_output["recv_data"]
    assert error == expected_output["error"]

@pytest.mark.parametrize("inputs, expected_output", [
    # Sample notary proof
    ({
        "public_values": ["value1", 123],
        "target_types": ["string", "uint256"],
    }, {
        "signature": "de25ff04e3201f94c8ef37131158cf1ba0472aa9380c08f7d845cddbea8afda3380ffc7052a822baa1ab92ad96831fb30f8cf08db775535698b18ff4e510dae11c",
        "serialized_values": ["value1", "123"]
    }),
])
def test_sign_and_serialize_values(inputs, expected_output):
    signature, serialized_values = TLSNProofVerifier(
        payment_type={},
        circuit_type={},
        regex_patterns_map={},
        regex_target_types={},
        error_codes_map={}
    ).sign_and_serialize_values(inputs["public_values"], inputs["target_types"])

    assert signature == expected_output["signature"]
    assert serialized_values == expected_output["serialized_values"]
