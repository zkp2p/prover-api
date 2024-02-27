import os
from eth_account import Account
from eth_account.messages import encode_defunct
import hashlib

def sign_values_with_private_key(env_var_name, values):
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

    # Concatenate the values into a single string
    message_str = ''.join(map(str, values))

    # It's common to hash the message before signing for consistency and efficiency
    message_hashed = hashlib.sha256(message_str.encode('utf-8')).hexdigest()

    # Encode the message in a format that's compatible with Ethereum's signing mechanism
    message_encoded = encode_defunct(hexstr=message_hashed)

    # Sign the message
    signed_message = Account.sign_message(message_encoded, private_key=private_key)

    # Return the signature in hex format
    return signed_message.signature.hex()

# Usage example:
# 1. First, ensure you have set the environment variable with your private key.
#    For example, in your terminal: export MY_ETH_PRIVATE_KEY='yourprivatekeyhere'
# 2. Then, call the function with the name of your environment variable and the values you want to sign.
# values_to_sign = ['value1', 'value2', 'value3']
# signature = sign_values_with_private_key('MY_ETH_PRIVATE_KEY', values_to_sign)
# print(signature)
