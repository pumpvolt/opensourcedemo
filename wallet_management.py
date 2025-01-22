from solders.keypair import Keypair #type: ignore
import json
import os
from base58 import b58encode #type: ignore
def generate_wallets(num_wallets=19):
    wallets = []
    for _ in range(num_wallets):
        account = Keypair()
        wallet = {
            'public_key': str(account.pubkey()),
            'secret_key': b58encode(account.secret() + str(account.pubkey()).encode('utf-8')).decode('utf-8')
        }
        wallets.append(wallet)
    return wallets

def save_wallets_to_file(wallets, filename='wallets.json'):
    with open(filename, 'w') as f:
        json.dump(wallets, f, indent=4)

def load_wallets_from_file(filename='wallets.json'):
    with open(filename, 'r') as f:
        wallets = json.load(f)
    return wallets

# Example usage
if not os.path.exists('wallets.json'):
    wallets = generate_wallets()
    save_wallets_to_file(wallets)
    print(f"Generated and saved {len(wallets)} wallets.")
else:
    wallets = load_wallets_from_file()
    print(f"Loaded {len(wallets)} wallets.")

