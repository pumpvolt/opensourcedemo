import requests
import os
from dotenv import load_dotenv

load_dotenv()

def generate_gpt_description(wallets):
    """Generate a description for the bundle using GPT."""
    prompt = f"Generate a creative description for a bundle containing {len(wallets)} wallets."
    return generate_gpt_response(prompt)

class PumpFunAPI:
    def __init__(self):
        self.api_url = os.getenv('PUMPFUN_API_URL')
        self.api_key = os.getenv('PUMPFUN_API_KEY')
        self.api_secret = os.getenv('PUMPFUN_API_SECRET')
        
    def create_bundle(self, wallets):
        """Create a bundle with multiple wallets and a GPT-generated description."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        gpt_description = generate_gpt_description(wallets)
        
        payload = {
            'wallets': [w['public_key'] for w in wallets],
            'bundle_name': os.getenv('PUMPFUN_API_BUNDLE_NAME'),
            'description': gpt_description,
            'price': os.getenv('PUMPFUN_API_BUNDLE_PRICE')
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/bundles",
                headers=headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
            
    def launch_bundle(self, bundle_id):
        """Launch a specific bundle"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/bundles/{bundle_id}/launch",
                headers=headers
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)} 

    def execute_bundled_trades(self, action, wallets, params):
        """Execute bundled trades for buying, selling, or moving liquidity"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'action': action,
            'wallets': [w['public_key'] for w in wallets],
            'params': params
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/execute_bundled_trades",
                headers=headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)} 