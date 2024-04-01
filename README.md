# prover-api

## Setup

1. Clone the repository
2. Setup virtual environment using `python3 -m venv venv`
3. Install the required dependencies using `pip install -r requirements.txt` 
4. Set `.env` file within each payment type subdirectory before running tests
5. `cd tlsn-verifier` and run `cargo build --release` to build the rust verifier
6. For testing, run `pytest` while back in the root folder