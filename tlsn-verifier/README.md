## Run

```bash
cargo build --release
./target/release/tlsn-verifier ../certs/notary.pub ../proofs/revolut/registration_proof_new_notary_key.json ../tlsn_verify_outputs/send_recv_data.txt ../tlsn_verify_outputs/recv_data.txt
```