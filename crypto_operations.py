from solders.keypair import Keypair #type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

def sign_message(message: str, keypair: Keypair) -> bytes:
    """Sign a message using a Solana keypair"""
    message_bytes = message.encode('utf-8')
    signature = keypair.sign_message(message_bytes)
    return signature

# Example usage
secret_key = Keypair.from_base58_string(os.getenv('SECRET_KEY'))
message = "This is a test message."
signature = sign_message(message, secret_key)
print(f"Signature: {signature}") 