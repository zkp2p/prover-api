# Use an existing Docker image as a base
FROM rust:1.76.0

# # Update the package list and install necessary dependencies
RUN apt-get update && \
    apt install -y cmake build-essential pkg-config libssl-dev libgmp-dev libsodium-dev nasm


RUN mkdir -p /root/prover-api/proofs
RUN mkdir -p /root/prover-api/tlsn_verify_outputs
RUN mkdir -p /root/prover-api/tlsn-verifier

# COPY ./tlsn-verifier/target/release/tlsn-verifier /root/prover-api/tlsn-verifier/target/release/tlsn-verifier
# RUN chmod +x /root/prover-api/tlsn-verifier/target/release/tlsn-verifier

COPY ./tlsn-verifier/ /root/prover-api/tlsn-verifier
WORKDIR /root/prover-api/tlsn-verifier
RUN cargo build --release

WORKDIR /root/prover-api