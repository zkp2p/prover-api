from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hmac import HMAC

def P_hash(secret, seed, hash_algorithm, length):
    backend = default_backend()
    result = b''
    hmac = HMAC(secret, hash_algorithm(), backend)
    hmac.update(seed)
    A = hmac.finalize()

    while len(result) < length:
        hmac = HMAC(secret, hash_algorithm(), backend)
        hmac.update(A + seed)
        current_hash = hmac.finalize()
        result += current_hash
        if len(result) >= length:
            break
        # Update A for the next iteration
        hmac = HMAC(secret, hash_algorithm(), backend)
        hmac.update(A)
        A = hmac.finalize()

    return result[:length]

def tls_prf(secret, label, seed, length):
    """
    TLS 1.2 Pseudorandom function (PRF) combining multiple HMAC-SHA256 hash outputs.
    """
    seed = label.encode() + seed
    return P_hash(secret, seed, hashes.SHA256, length)

def main():
    # Example values (replace with actual secrets and randoms)
    master_secret = bytes.fromhex('f320c7912c86dc450f70ccedb59ff946b4efa41eb24945787b1b98de28d679f1de3f6ffb37f5dc844c73f5047fc0504d')
    client_random = bytes.fromhex('7300aa80693888f12a86c86f067453c0c0b492a6ef7315ce74c7338a05fa3c4b')
    # without timestamp 693888f12a86c86f067453c0c0b492a6ef7315ce74c7338a05fa3c4b
    server_random = bytes.fromhex('4f8ed0f76c7b55ed59699bb85272d3a5df770eea8721dfc857850f4de12d236c')
    # without timestamp server_random = bytes.fromhex('6c7b55ed59699bb85272d3a5df770eea8721dfc857850f4de12d236c')

    key_block_length = 88  # As calculated: 2 * (32 + 12) bytes for keys and IVs

    # Generate the key block
    key_block = tls_prf(master_secret, 'key expansion', client_random + server_random, key_block_length)

    client_write_key = key_block[:32]
    server_write_key = key_block[32:64]
    client_write_iv = key_block[64:76]
    server_write_iv = key_block[76:88]

    print("Client Write Key:", client_write_key.hex())
    print("Server Write Key:", server_write_key.hex())
    print("Client Write IV:", client_write_iv.hex())
    print("Server Write IV:", server_write_iv.hex())

if __name__ == "__main__":
    main()
