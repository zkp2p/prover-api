# Todo: Add refresh logic.

# Folder structure
# /root/
#       zk-p2p/
#           circuits-circom/
#               circuits/${payment_type}/build/
#                   hdfc_${email_type}/
#                       hdfc_${email_type}.zkey
#                       hdfc_${email_type}_js/
#                           generate_witness.js
#                           witness_calculator.js
#                           hdfc_${email_type}.wasm
#                           witness_${email_type}_${nonce}.wtns
#                       hdfc_${email_type}_cpp/
#                           hdfc_${email_type}
#       prover-api/
#           proofs/
#               rapidsnark_proof_${email_type}_${nonce}.json
#               rapidsnark_public_${email_type}_${nonce}.json
#           received_eml/
#               hdfc_${email_type}_${nonce}.eml
#           inputs/
#               input_hdfc_${email_type}_${nonce}.json
#           circom_proofgen.sh
#       rapidsnark/
#           build/
#               prover



# Use the official Rust image as the base image
FROM rust:latest
ARG ZKP2P_BRANCH_NAME=develop
ARG ZKP2P_VERSION=v2.5/v0.2.1
ARG PROVER_API_BRANCH_NAME=sachin/upi
ARG PAYMENT_TYPE=hdfc
ARG PAYMENT_ROOT_DIR=/root/zk-p2p/circuits-circom/circuits/${PAYMENT_TYPE}
ARG BUILD_DIR=${PAYMENT_ROOT_DIR}/build

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
WORKDIR ${PAYMENT_ROOT_DIR}
RUN yarn install
RUN yarn add tsx
WORKDIR /root/zk-p2p/circuits-circom/package
RUN yarn install

# Pull JS .wasm from S3 and place them in js folders
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send_js https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send.wasm --quiet
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration_js https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration.wasm --quiet

# Pull C .dat from S3 and place them in cpp folders
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send_cpp https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send.dat --quiet
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration_cpp https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration.dat --quiet

# Pull C witness gen binary from S3 and place them in cpp folders
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send_cpp https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send --quiet
# RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration_cpp https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration --quiet

# Make cpp files executable
# RUN chmod +x ${BUILD_DIR}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send_cpp/${PAYMENT_TYPE}_send
# RUN chmod +x ${BUILD_DIR}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration_cpp/${PAYMENT_TYPE}_registration

# Pull keys from S3
RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_send https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_send/${PAYMENT_TYPE}_send.zkey --quiet
RUN wget -P ${BUILD_DIR}/${PAYMENT_TYPE}_registration https://zk-p2p.s3.amazonaws.com/${ZKP2P_VERSION}/${PAYMENT_TYPE}_registration/${PAYMENT_TYPE}_registration.zkey --quiet

# Clone the prover-api repository at the latest commit and set it as the working directory
RUN git clone --branch ${PROVER_API_BRANCH_NAME} --single-branch https://github.com/zkp2p/prover-api /root/prover-api
WORKDIR /root/prover-api

# Install pytho, pip and requirements to run coordinator.py (Not required for modal)
# RUN apt-get install -y python3 python-is-python3 python3-pip python3-venv
# RUN python3 -m venv /venv
# # Activate the virtual environment and install requirements
# RUN /venv/bin/pip install --no-cache-dir -r /root/prover-api/requirements.txt
# RUN apt-get install vim -y