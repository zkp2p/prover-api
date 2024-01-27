def run_prove_process(payment_type:str, circuit_type:str, nonce: str, intent_hash: str, c_witness_gen: str):
    print('Running prove email')
    
    import subprocess 

    # Run the circom proofgen script
    result = subprocess.run(
        [
            '/root/prover-api/circom_proofgen.sh', 
            payment_type, 
            circuit_type, 
            nonce, intent_hash, 
            c_witness_gen
        ],
        capture_output=True, 
        text=True
    )
    print(result.stdout)
    return result
    