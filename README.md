# prover-api

## Setup

1. Clone the repository
2. Setup virtual environment using `python3 -m venv venv`
3. Install the required dependencies using `pip install -r requirements.txt` 
4. `cp .env.example .env` and set `.env` file within each payment type subdirectory before running tests. For `wise` and `utils`, set `CUSTOM_PROVER_API_PATH` to your local path of the prover-api directory and `VERIFIER_PRIVATE_KEY` to any private key you want to use for testing.
5. `cd tlsn-verifier` and run `cargo build --release` to build the rust verifier
6. For testing, run `pytest` while back in the root folder

## Deployment
TODO