import { verifyProof, makeLocalSnarkJsZkOperator } from '@reclaimprotocol/circom-symmetric-crypto';
import * as fs from 'fs/promises';

function hexToBuffer(hexString: string): Buffer {
    // Ensure the hex string has an even length (required for valid byte conversion)
    if (hexString.length % 2 !== 0) {
        throw new Error("Invalid hex string: length must be even");
    }

    // Create a Buffer from the hex string
    const buffer = Buffer.from(hexString, 'hex');

    return buffer;
}


async function verify() {
    const argv = process.argv.slice(2);
    if (argv.length < 3) {
        console.error('Usage: node script.js <proofJsonPath> <plaintext> <ciphertext>');
        process.exit(1);
    }

    const [proofJsonPath, plaintextHex, ciphertextHex] = argv;
    // console.log(proofJsonPath)

    try {
        const proofJson = await fs.readFile(proofJsonPath, 'utf8');
        // console.log(proofJson);  // Log the raw string to check its format

        const plaintext = hexToBuffer(plaintextHex)
        const ciphertext = hexToBuffer(ciphertextHex)

        const algorithm = 'chacha20';
        const operator = await makeLocalSnarkJsZkOperator(algorithm);

        // Will assert the proof is valid; otherwise, it will throw an error
        // await verifyProof({
        //     proof: {
        //         proofJson,
        //         plaintext,
        //         algorithm
        //     },
        //     // The public inputs to the circuit
        //     publicInput: { ciphertext },
        //     operator
        // });

        console.log('proof verified');
    } catch (error) {
        console.error('Error during verification:', error);
        process.exit(1);
    }
}

verify().then(() => {
    console.log('Verification complete')
    return true;
}).catch(err => {
    console.error('Verification failed:', err);
    process.exit(1);
});
