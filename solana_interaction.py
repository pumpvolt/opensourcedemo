from solana.rpc.api import Client
from solders.keypair import Keypair #type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.instruction import Instruction #type: ignore
import json
import time
from solana.rpc.commitment import Processed, Confirmed
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
import os
from dotenv import load_dotenv
from base58 import b58decode  # Add this import at the top
from solders.system_program import TransferParams, transfer  # Add this import
from solana.rpc.types import  TxOpts
from solders.message import MessageV0 #type: ignore # Add this import
from solders.transaction import VersionedTransaction #type: ignore  # Add this import

load_dotenv()

def get_wallet_balance(wallet_address):
    client = Client("https://api.mainnet-beta.solana.com")
    wallet_address = wallet_address.strip()  # Clean the address
    print(f"Wallet address: {wallet_address} (Length: {len(wallet_address)})")  # Debugging
    # Convert base58 string to bytes
    try:
        public_key = Pubkey.from_string(wallet_address)
    except ValueError as e:
        print(f"Error creating public key: {e}")
        return None
    balance = client.get_balance(public_key)
    return balance.value

def send_transaction(sender_keypair, recipient_address, amount):
    send_transaction_client = Client("https://api.mainnet-beta.solana.com")
    
    # Check sender balance first
    sender_balance = send_transaction_client.get_balance(sender_keypair.pubkey()).value
    if sender_balance < amount:
        raise ValueError(f"Insufficient balance. Account has {sender_balance} lamports, but {amount} lamports are needed for the transaction.")
    
    # Create a versioned transaction
    recent_blockhash = send_transaction_client.get_latest_blockhash().value.blockhash
    
    # Create transfer instruction
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=sender_keypair.pubkey(),
            to_pubkey=Pubkey.from_string(recipient_address),
            lamports=amount
        )
    )
    
    # Compile message
    message = MessageV0.try_compile(
        payer=sender_keypair.pubkey(),
        instructions=[transfer_ix],
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash
    )
    
    # Create and sign transaction
    transaction = VersionedTransaction(message, [sender_keypair])
    
    # Send transaction
    response = send_transaction_client.send_transaction(
        transaction,
        opts=TxOpts(skip_preflight=False)
    )
    return response

# Example usage
wallet_address = os.getenv('WALLET_ADDRESS')
print(f"Wallet address: {wallet_address}")
balance = get_wallet_balance(wallet_address)
print(f"Wallet balance: {balance} lamports")

# Only proceed with transfer if there's enough balance
if balance > 1000000:  # Amount in lamports
    sender_keypair = Keypair.from_base58_string(os.getenv('SECRET_KEY'))
    recipient_address = os.getenv('RECIPIENT_ADDRESS')
    amount = 1000000  # Amount in lamports
    try:
        response = send_transaction(sender_keypair, recipient_address, amount)
        print(f"Transaction response: {response}")
    except ValueError as e:
        print(f"Error: {e}")
else:
    print("Insufficient balance to perform transfer") 