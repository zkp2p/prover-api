import os
from web3 import Web3
from eth_abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct

def encode_and_hash(args, types):
    """
    Encode arguments according to specified types and hash the result using keccak256.
    
    :param args: The values to encode.
    :param types: The Solidity types of the arguments.
    :return: The keccak256 hash of the encoded arguments.
    """
    # Encode the arguments
    encoded = encode(types, args)
    print('Encode packed values', encoded)

    # Hash the encoded arguments
    hashed = Web3.keccak(encoded)

    return hashed.hex()


def sign_values_with_private_key(env_var_name, values, types):
    """
    Loads an Ethereum private key from an environment variable,
    signs a concatenated string of the provided values, and returns the signature.

    :param env_var_name: The name of the environment variable holding the private key.
    :param values: An array of values to sign.
    :return: The signature of the concatenated values.
    """
    # Load the private key from the environment variable
    private_key = os.getenv(env_var_name)
    if not private_key:
        raise ValueError(f"Environment variable '{env_var_name}' not found or empty.")

    # Encode the arguments according to their specified types and hash them
    message = encode_and_hash(values, types)
    print('Hashed encoded message:', message)

    # Sign the message
    message_encoded = encode_defunct(hexstr=message)
    print('Message Encoded (Signed):', message_encoded)
    signed_message = Account.sign_message(message_encoded, private_key=private_key)

    # Return the signature in hex format
    return signed_message.signature.hex()
