#!/bin/bash

# Folder structure
# /root/
#       zk-p2p/
#           circuits-circom/
#               build/
#                   ${payment_type}_${circuit_type}/
#                       ${payment_type}_${circuit_type}.wasm
#                       ${payment_type}_${circuit_type}.zkey
#                       ${payment_type}_${circuit_type}_js/
#                           generate_witness.js
#                           witness_${payment_type}_${circuit_type}_${nonce}.wtns
#                       ${payment_type}_${circuit_type}_cpp/
#                           ${payment_type}_${circuit_type}
#                       ${payment_type}_${circuit_type}_cpp/
#                           ${payment_type}_${circuit_type}
#       prover-api/
#           proofs/
#               rapidsnark_proof_${payment_type}_${circuit_type}_${nonce}.json
#               rapidsnark_public_${payment_type}_${circuit_type}_${nonce}.json
#           received_eml/
#               ${payment_type}_${circuit_type}_${nonce}.eml
#           inputs/
#               input_${payment_type}_${circuit_type}_${nonce}.json
#           circom_proofgen.sh
#       rapidsnark/
#           build/
#               prover

payment_type=$1
circuit_type=$2
nonce=$2
intent_hash=$3
c_witness_gen=${4:-false}

HOME="${MODAL_HOME_PATH}"
zk_p2p_path="${MODAL_ZK_P2P_CIRCOM_PATH}"
eml_dir_path="${MODAL_INCOMING_EML_PATH}"
prover_output_path="${eml_dir_path}/../proofs/"

circuit_name=${payment_type}_${circuit_type}
eml_path="${eml_dir_path}/${circuit_name}_${nonce}.eml"
input_email_path="${eml_dir_path}/../inputs/input_${circuit_name}_${nonce}.json"
build_dir="${zk_p2p_path}/circuits-circom/build/${circuit_name}"
witness_path="${build_dir}/witness_${circuit_name}_${nonce}.wtns"
proof_path="${prover_output_path}/rapidsnark_proof_${circuit_name}_${nonce}.json"
public_path="${prover_output_path}/rapidsnark_public_${circuit_name}_${nonce}.json"

echo "npx ${zk_p2p_path}/circuits-circom/node_modules/.bin/tsx ${zk_p2p_path}/circuits-circom/scripts/generate_input.ts --email_file='${eml_path}' --payment_type='${payment_type}' --circuit_type='${circuit_type}' --nonce='${nonce}' --intent_hash='${intent_hash}'"
npx ${zk_p2p_path}/circuits-circom/node_modules/.bin/tsx "${zk_p2p_path}/circuits-circom/scripts/generate_input.ts" --email_file="${eml_path}" --payment_type="${payment_type}" --circuit_type="${circuit_type}" --nonce="${nonce}" --intent_hash="${intent_hash}" | tee /dev/stderr
status_inputgen=$?

# Todo: Is status_inputgen set to anything?
echo "Finished input gen! Status: ${status_inputgen}"
if [ $status_inputgen -ne 0 ]; then
    echo "generate_input.ts failed with status: ${status_inputgen}"
    exit 1
fi

if [ "$c_witness_gen" = true ]; then
    echo "Performing c witness gen!"
    echo "${build_dir}/${circuit_name}_cpp/${circuit_name} ${input_email_path} ${witness_path}"
    "${build_dir}/${circuit_name}_cpp/${circuit_name}" "${input_email_path}" "${witness_path}"
    status_cwitgen=$?

    if [ $status_cwitgen -ne 0 ]; then
        echo "C based witness gen failed with status: ${status_cwitgen}"
        exit 1
    fi
else 
    echo "Performing js witness gen!"
    echo "node ${build_dir}/${circuit_name}_js/generate_witness.js ${build_dir}/${circuit_name}_js/${circuit_name}.wasm ${input_email_path} ${witness_path}"
    node "${build_dir}/${circuit_name}_js/generate_witness.js" "${build_dir}/${circuit_name}_js/${circuit_name}.wasm" "${input_email_path}" "${witness_path}"  | tee /dev/stderr
    status_jswitgen=$?
    echo "status_jswitgen: ${status_jswitgen}"

    if [ $status_jswitgen -ne 0 ]; then
        echo "generate_witness.js failed with status: ${status_jswitgen}"
        exit 1
    fi
fi

echo "ldd ${HOME}/rapidsnark/build/prover"
ldd "${HOME}/rapidsnark/build/prover"
status_lld=$?

if [ $status_lld -ne 0 ]; then
    echo "lld prover dependencies failed with status: ${status_lld}"
    exit 1
fi

echo "${HOME}/rapidsnark/build/prover ${build_dir}/${circuit_name}.zkey ${witness_path} ${proof_path} ${public_path}"
"${HOME}/rapidsnark/build/prover" "${build_dir}/${circuit_name}.zkey" "${witness_path}" "${proof_path}" "${public_path}"  | tee /dev/stderr
status_prover=$?

if [ $status_prover -ne 0 ]; then
    echo "prover failed with status: ${status_prover}"
    exit 1
fi

echo "Finished proofgen! Status: ${status_prover}"