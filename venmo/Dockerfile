# Todo: Add refresh logic.

# Folder structure
# /root/
#       zk-p2p/
#           circuits-circom/
#               build/
#                   venmo_${email_type}/
#                       venmo_${email_type}.zkey
#                       venmo_${email_type}_js/
#                           generate_witness.js
#                           witness_calculator.js
#                           venmo_${email_type}.wasm
#                           witness_${email_type}_${nonce}.wtns
#                       venmo_${email_type}_cpp/
#                           venmo_${email_type}
#       prover-api/
#           proofs/
#               rapidsnark_proof_${email_type}_${nonce}.json
#               rapidsnark_public_${email_type}_${nonce}.json
#           received_eml/
#               venmo_${email_type}_${nonce}.eml
#           inputs/
#               input_venmo_${email_type}_${nonce}.json
#           circom_proofgen.sh
#       rapidsnark/
#           build/
#               prover



# Use the official Rust image as the base image
FROM rust:latest
ARG ZKP2P_BRANCH_NAME=develop
ARG ZKP2P_VERSION=v0.1.0
ARG PROVER_API_BRANCH_NAME=sachin/v0.1.0

# Update the package list and install necessary dependencies
RUN apt-get update && \
    apt install -y cmake build-essential pkg-config libssl-dev libgmp-dev libsodium-dev nasm

# Install Node.js 16.x and Yarn
ENV NODE_VERSION=16.19.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version
RUN npm install -g yarn
RUN npm install -g typescript

# Clone and build rapidsnark
RUN  git clone https://github.com/Divide-By-0/rapidsnark /root/rapidsnark
WORKDIR /root/rapidsnark
RUN npm install
RUN git submodule init
RUN git submodule update
RUN npx task createFieldSources
RUN npx task buildPistache
RUN npx task buildProver
RUN chmod +x /root/rapidsnark/build/prover
WORKDIR /root/

# TODO: Instead we could just copy the build folder from the local machine
# COPY ./rapidsnark/build /rapidsnark/build

# Clone zk p2p repository at the latest commit and set it as the working directory
RUN git clone https://github.com/zkp2p/zk-p2p -b ${ZKP2P_BRANCH_NAME} /root/zk-p2p
WORKDIR /root/zk-p2p/circuits-circom
RUN yarn install
RUN yarn add tsx

# Pull keys from S3
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_send https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_send/venmo_send.zkey --quiet
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_registration https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_registration/venmo_registration.zkey --quiet

# Pull C witness gen binary from S3
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_send/venmo_send_cpp https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_send/venmo_send --quiet
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_send/venmo_send_cpp https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_send/venmo_send.dat --quiet
RUN chmod +x /root/zk-p2p/circuits-circom/build/venmo_send/venmo_send_cpp/venmo_send
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_registration/venmo_registration_cpp https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_registration/venmo_registration --quiet
RUN wget -P /root/zk-p2p/circuits-circom/build/venmo_registration/venmo_registration_cpp https://zk-p2p.s3.amazonaws.com/v2/${ZKP2P_VERSION}/venmo_registration/venmo_registration.dat --quiet
RUN chmod +x /root/zk-p2p/circuits-circom/build/venmo_registration/venmo_registration_cpp/venmo_registration

# Clone the prover-api repository at the latest commit and set it as the working directory
RUN git clone --branch ${PROVER_API_BRANCH_NAME} --single-branch https://github.com/zkp2p/prover-api /root/prover-api
WORKDIR /root/prover-api

# Make necessary files executable
RUN chmod +x /root/prover-api/circom_proofgen.sh

# Copy .env.example to .env
RUN cp /root/prover-api/.env.example /root/prover-api/.env


# Install pytho, pip and requirements to run coordinator.py (Not required for modal)
# RUN apt-get install -y python3 python-is-python3 python3-pip python3-venv
# RUN python3 -m venv /venv
# # Activate the virtual environment and install requirements
# RUN /venv/bin/pip install --no-cache-dir -r /root/prover-api/requirements.txt