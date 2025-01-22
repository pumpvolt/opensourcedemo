from flask import Flask, render_template, request, jsonify
from solana_interaction import get_wallet_balance, send_transaction
from gpt_integration import generate_gpt_response
from crypto_operations import sign_message
from dotenv import load_dotenv
import os
from wallet_management import generate_wallets, save_wallets_to_file, load_wallets_from_file
from pumpfun_integration import PumpFunAPI
import openai
from solders.keypair import Keypair  # type: ignore
from base58 import b58decode  # type: ignore

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

pumpfun_api = PumpFunAPI()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/balance', methods=['POST'])
def check_balance():
    try:
        wallet_address = request.form['wallet_address']
        balance = get_wallet_balance(wallet_address)
        return jsonify({'balance': balance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send', methods=['POST'])
def send_sol():
    try:
        sender_keypair = request.form['sender_keypair']
        recipient_address = request.form['recipient_address']
        amount = int(request.form['amount'])
        response = send_transaction(sender_keypair, recipient_address, amount)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gpt', methods=['POST'])
def gpt_response():
    try:
        prompt = request.form['prompt']
        response = generate_gpt_response(prompt)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sign', methods=['POST'])
def sign():
    try:
        message = request.form['message']
        private_key = request.form['private_key']
        signature = sign_message(message, private_key)
        return jsonify({'signature': signature.hex()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_wallets', methods=['POST'])
def generate_wallets_route():
    try:
        num_wallets = int(request.form.get('num_wallets', 19))
        
        # Try to load existing wallets
        existing_wallets = []
        try:
            existing_wallets = load_wallets_from_file()
        except:
            existing_wallets = []
        
        # Calculate how many new wallets we need
        additional_wallets = num_wallets - len(existing_wallets)
        
        if additional_wallets > 0:
            # Generate only the additional wallets needed
            new_wallets = generate_wallets(additional_wallets)
            # Combine with existing wallets
            all_wallets = existing_wallets + new_wallets
            save_wallets_to_file(all_wallets)
            return jsonify({
                'message': f'Added {additional_wallets} new wallets. Total wallets: {len(all_wallets)}',
                'new_wallets': additional_wallets,
                'total_wallets': len(all_wallets)
            })
        else:
            return jsonify({
                'message': f'Already have {len(existing_wallets)} wallets. No new wallets needed.',
                'new_wallets': 0,
                'total_wallets': len(existing_wallets)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/launch_bundle', methods=['POST'])
def launch_bundle_route():
    try:
        api_key = request.form['api_key']
        wallets = load_wallets_from_file()
        client = OpenAI(api_key=api_key)
        response = launch_bundle(wallets, api_key)
        return jsonify({'response': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bundled_launch', methods=['POST'])
def bundled_launch():
    try:
        wallets = load_wallets_from_file()
        # Generate a GPT response for additional insights or recommendations
        gpt_insight = generate_gpt_response("Provide insights for launching a bundle with these wallets.")
        response = pumpfun_api.create_bundle(wallets)
        return jsonify({'response': response, 'gpt_insight': gpt_insight})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coordinated_sell', methods=['POST'])
def coordinated_sell():
    try:
        bundle_id = request.form['bundle_id']
        response = pumpfun_api.launch_bundle(bundle_id)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    try:
        user_question = request.form['question']
        gpt_response = generate_gpt_response(user_question)
        return jsonify({'response': gpt_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_wallets', methods=['GET'])
def get_wallets():
    try:
        wallets = load_wallets_from_file()
        return jsonify({'wallets': wallets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_wallet_details', methods=['GET'])
def get_wallet_details():
    try:
        wallets = load_wallets_from_file()
        wallet_details = []
        for wallet in wallets:
            balance = get_wallet_balance(wallet['public_key'])
            wallet_details.append({
                'public_key': wallet['public_key'],
                'secret_key': wallet['secret_key'],
                'balance': balance
            })
        return jsonify({'wallets': wallet_details})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask_gpt_about_wallets', methods=['POST'])
def ask_gpt_about_wallets():
    try:
        question = request.form['question']
        wallets = load_wallets_from_file()
        
        # Create a context-aware prompt
        wallet_context = f"Context: There are {len(wallets)} wallets in the system. "
        wallet_context += "These are Solana wallets that can be bundled for coordinated actions. "
        
        prompt = f"{wallet_context}\nQuestion: {question}\nPlease provide a detailed answer about the wallets and bundling strategy."
        
        response = generate_gpt_response(prompt)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/suggest_bundle_strategy', methods=['POST'])
def suggest_bundle_strategy():
    try:
        wallets = load_wallets_from_file()
        wallet_details = []
        total_balance = 0
        
        for wallet in wallets:
            balance = get_wallet_balance(wallet['public_key'])
            total_balance += float(balance)
            wallet_details.append({
                'public_key': wallet['public_key'],
                'balance': balance
            })

        prompt = f"""
        Analyze the following wallet data and suggest an optimal bundling strategy:
        - Total wallets: {len(wallets)}
        - Total balance: {total_balance} SOL
        - Average balance: {total_balance/len(wallets)} SOL

        Consider factors like:
        1. Risk distribution
        2. Transaction timing
        3. Balance distribution
        4. Market impact

        Provide a detailed recommendation for bundling these wallets.
        """
        
        strategy = generate_gpt_response(prompt)
        return jsonify({'strategy': strategy})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fund_wallets', methods=['POST'])
def fund_wallets():
    try:
        amount = float(request.form.get('amount', 0))
        admin_secret = os.getenv('SECRET_KEY')
        admin_keypair = Keypair.from_base58_string(admin_secret)
        admin_wallet_address = os.getenv('WALLET_ADDRESS')
        
        # Get admin wallet balance first
        admin_balance = get_wallet_balance(admin_wallet_address)
        if admin_balance is None:
            return jsonify({
                'error': 'Failed to fetch admin wallet balance',
                'insufficient_funds': True
            }), 400
        
        # Calculate total needed (amount * number of wallets)
        wallets = load_wallets_from_file()
        total_needed = amount * len(wallets)
        
        # Check if admin has enough balance
        if admin_balance < total_needed:
            return jsonify({
                'error': f'Insufficient funds in admin wallet. Available: {admin_balance} SOL, Required: {total_needed} SOL',
                'insufficient_funds': True,
                'available_balance': admin_balance,
                'required_balance': total_needed
            }), 400
            
        # Continue with existing funding logic...
        results = []
        for wallet in wallets:
            try:
                response = send_transaction(
                    sender_keypair=admin_keypair,
                    recipient_address=wallet['public_key'],
                    amount=amount
                )
                results.append({
                    'wallet': wallet['public_key'],
                    'status': 'success',
                    'amount': amount
                })
            except Exception as e:
                results.append({
                    'wallet': wallet['public_key'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Funding complete. {len([r for r in results if r["status"] == "success"])} wallets funded successfully.',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_admin_wallet', methods=['GET'])
def get_admin_wallet():
    try:
        admin_address = os.getenv('WALLET_ADDRESS')
        balance = get_wallet_balance(admin_address)
        return jsonify({
            'address': admin_address,
            'balance': balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_pumpfun_stats', methods=['GET'])
def get_pumpfun_stats():
    try:
        # This is a placeholder - integrate with actual PumpFun API
        stats = {
            'bundle_stats': {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'data': [12, 19, 15, 25, 22, 30, 28],
                'total_bundles': 151,
                'active_bundles': 45,
                'success_rate': 92
            },
            'performance': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'returns': [5.2, 7.8, 6.5, 8.9],
                'volume': [1200, 1800, 1500, 2200]
            }
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_section_content', methods=['GET'])
def get_section_content():
    section = request.args.get('section', 'dashboard')
    try:
        if section == 'dashboard':
            stats = {
                'total_wallets': len(load_wallets_from_file()),
                'bundle_stats': {
                    'total_bundles': 151,
                    'active_bundles': 45,
                    'success_rate': 92
                },
                'performance': {
                    'daily_volume': 2500,
                    'weekly_growth': 15.4
                }
            }
            return jsonify(stats)
        elif section == 'wallets':
            wallets = load_wallets_from_file()
            return jsonify({'wallets': wallets})
        elif section == 'bundler':
            return jsonify({
                'bundle_stats': {
                    'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'data': [12, 19, 15, 25, 22, 30, 28]
                }
            })
        elif section == 'settings':
            return jsonify({
                'settings': {
                    'rpc_url': os.getenv('RPC_URL'),
                    'program_id': os.getenv('PUMP_FUN_PROGRAM'),
                    'network': 'mainnet-beta'
                }
            })
        else:
            return jsonify({'error': 'Invalid section'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/create_bundle', methods=['POST'])
def create_bundle():
    try:
        wallets = load_wallets_from_file()
        response = pumpfun_api.create_bundle(wallets)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/launch_bundle', methods=['POST'])
def launch_bundle():
    try:
        bundle_id = request.form['bundle_id']
        response = pumpfun_api.launch_bundle(bundle_id)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/execute_bundled_trades', methods=['POST'])
def execute_bundled_trades():
    try:
        action = request.form['action']
        wallets = load_wallets_from_file()
        params = request.form.get('params', {})
        response = pumpfun_api.execute_bundled_trades(action, wallets, params)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 