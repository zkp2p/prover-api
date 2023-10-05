#!/bin/bash

# Folder structure
# /root/
#       zk-p2p/
#           circuits-circom/
#               build/
#                   venmo_${email_type}/
#                       venmo_${email_type}.wasm
#                       venmo_${email_type}.zkey
#                       venmo_${email_type}_js/
#                           generate_witness.js
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

email_type=$1
nonce=$2

HOME="${MODAL_HOME_PATH}"
zk_p2p_path="${MODAL_ZK_P2P_CIRCOM_PATH}"
venmo_eml_dir_path="${MODAL_INCOMING_EML_PATH}"
prover_output_path="${venmo_eml_dir_path}/../proofs/"

circuit_name=venmo_${email_type}
venmo_eml_path="${venmo_eml_dir_path}/venmo_${email_type}_${nonce}.eml"
input_email_path="${venmo_eml_dir_path}/../inputs/input_venmo_${email_type}_${nonce}.json"
build_dir="${zk_p2p_path}/circuits-circom/build/${circuit_name}"
witness_path="${build_dir}/witness_${email_type}_${nonce}.wtns"
proof_path="${prover_output_path}/rapidsnark_proof_${email_type}_${nonce}.json"
public_path="${prover_output_path}/rapidsnark_public_${email_type}_${nonce}.json"

echo "npx ${zk_p2p_path}/circuits-circom/node_modules/.bin/tsx ${zk_p2p_path}/circuits-circom/scripts/generate_input.ts --email_file='${venmo_eml_path}' --email_type='${email_type}' --nonce='${nonce}'"
npx ${zk_p2p_path}/circuits-circom/node_modules/.bin/tsx "${zk_p2p_path}/circuits-circom/scripts/generate_input.ts" --email_file="${venmo_eml_path}" --email_type="${email_type}" --nonce="${nonce}" | tee /dev/stderr
status_inputgen=$?

echo "Finished input gen! Status: ${status_inputgen}"
if [ $status_inputgen -ne 0 ]; then
    echo "generate_input.ts failed with status: ${status_inputgen}"
    exit 1
fi

echo "node ${build_dir}/${circuit_name}_js/generate_witness.js ${build_dir}/${circuit_name}_js/${circuit_name}.wasm ${input_email_path} ${witness_path}"
node "${build_dir}/${circuit_name}_js/generate_witness.js" "${build_dir}/${circuit_name}_js/${circuit_name}.wasm" "${input_email_path}" "${witness_path}"  | tee /dev/stderr
status_jswitgen=$?
echo "status_jswitgen: ${status_jswitgen}"

if [ $status_jswitgen -ne 0 ]; then
    echo "generate_witness.js failed with status: ${status_jswitgen}"
    exit 1
fi

# echo "/${build_dir}/${circuit_name}_cpp/${circuit_name} ${input_email_path} ${witness_path}"
# "/${build_dir}/${circuit_name}_cpp/${circuit_name}" "${input_email_path}" "${witness_path}"
# status_c_wit=$?

# echo "Finished C witness gen! Status: ${status_c_wit}"
# if [ $status_c_wit -ne 0 ]; then
#     echo "C based witness gen failed with status (might be on machine specs diff than compilation): ${status_c_wit}"
#     exit 1
# fi

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