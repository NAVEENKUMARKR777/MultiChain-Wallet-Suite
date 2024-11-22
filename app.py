from flask import Flask, render_template, request, jsonify
from wallet_manager import MultiChainWallet
from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import json
from pathlib import Path

app = Flask(__name__)
load_dotenv()

# Initialize wallet manager
wallet_manager = None
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL')))

def is_valid_eth_address(address):
    """Check if the address is a valid Ethereum address"""
    if not address.startswith('0x'):
        return False
    try:
        return w3.isAddress(address) and len(address) == 42
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_wallet', methods=['POST'])
def generate_wallet():
    global wallet_manager
    try:
        # Get mnemonic if provided, otherwise generate new
        mnemonic = request.form.get('mnemonic', None)
        wallet_manager = MultiChainWallet(mnemonic_phrase=mnemonic, testnet=True)
        
        # Generate wallets
        wallets = wallet_manager.generate_all_wallets()
        
        return jsonify({
            'success': True,
            'mnemonic': wallet_manager.mnemonic,
            'wallets': wallets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    try:
        to_address = request.form['to_address']
        amount = float(request.form['amount'])
        chain = request.form['chain']
        
        if chain != 'ethereum':
            return jsonify({
                'success': False,
                'error': 'Only Ethereum transactions are supported currently'
            })
        
        # Validate Ethereum address
        if not is_valid_eth_address(to_address):
            return jsonify({
                'success': False,
                'error': 'Invalid Ethereum address format. Address should start with 0x and be 42 characters long.'
            })
        
        # Get the private key from the form
        private_key = request.form['private_key']
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
            
        # Convert amount to Wei
        value = w3.toWei(amount, 'ether')
        
        # Get gas settings from env
        gas_price_gwei = float(os.getenv('GAS_PRICE_GWEI', '0.1'))
        gas_price = w3.toWei(gas_price_gwei, 'gwei')
        
        # Use the minimum required gas for ETH transfers or estimate if it's a contract
        try:
            gas_limit = w3.eth.estimateGas({
                'to': to_address,
                'value': value,
                'from': Account.privateKeyToAccount(private_key).address
            })
            # Add a 10% buffer to the estimate
            gas_limit = int(gas_limit * 1.1)
        except:
            # If estimation fails, use the minimum gas for ETH transfers
            gas_limit = 21000
        
        # Get nonce with pending transactions included
        account = Account.privateKeyToAccount(private_key)
        nonce = w3.eth.getTransactionCount(account.address, 'pending')
        
        # Build transaction
        transaction = {
            'nonce': nonce,
            'to': to_address,
            'value': value,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': int(os.getenv('ETHEREUM_CHAIN_ID', 11155111))
        }
        
        # Sign transaction
        signed = Account.signTransaction(transaction, private_key)
        
        try:
            # Try to send the transaction
            tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        except Exception as e:
            if "already known" in str(e):
                # If transaction is already known, wait for it to be mined
                # or get the transaction hash from the error message
                try:
                    # Try to get existing transaction
                    pending_tx = w3.eth.getTransaction(nonce)
                    if pending_tx:
                        tx_hash = pending_tx['hash']
                    else:
                        raise Exception("Transaction already in mempool, please wait for it to be mined")
                except:
                    raise Exception("Transaction already in mempool, please wait for it to be mined")
            else:
                raise e
        
        return jsonify({
            'success': True,
            'transaction_hash': w3.toHex(tx_hash),
            'message': 'Transaction submitted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        address = request.form['address']
        chain = request.form['chain']
        
        if chain != 'ethereum':
            return jsonify({
                'success': False,
                'error': 'Only Ethereum balance checking is supported currently'
            })
        
        # Validate Ethereum address
        if not is_valid_eth_address(address):
            return jsonify({
                'success': False,
                'error': 'Invalid Ethereum address format. Address should start with 0x and be 42 characters long.'
            })
        
        balance = w3.eth.getBalance(address)
        balance_eth = w3.fromWei(balance, 'ether')
        
        return jsonify({
            'success': True,
            'balance': str(balance_eth),
            'currency': 'ETH'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/contracts', methods=['GET'])
def get_contracts():
    try:
        contracts_file = Path(__file__).parent / 'contracts' / 'deployed_contracts.json'
        with open(contracts_file, 'r') as f:
            contracts = json.load(f)
        return jsonify({
            'success': True,
            'contracts': contracts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/contract/multiwithdraw/send', methods=['POST'])
def multi_withdraw():
    try:
        # Get parameters
        private_key = request.form['private_key']
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
            
        recipients = request.form.getlist('recipients[]')
        amounts = [w3.toWei(float(amount), 'ether') for amount in request.form.getlist('amounts[]')]
        
        # Validate inputs
        if len(recipients) != len(amounts):
            raise ValueError("Recipients and amounts must have the same length")
        if not recipients or not amounts:
            raise ValueError("Recipients and amounts cannot be empty")
            
        # Load contract address
        contracts_file = Path(__file__).parent / 'contracts' / 'deployed_contracts.json'
        with open(contracts_file, 'r') as f:
            contracts = json.load(f)
        contract_address = contracts['MultiWithdraw']['sepolia']['address']
        
        # Calculate total amount
        total_amount = sum(amounts)
        
        # Get account
        account = Account.privateKeyToAccount(private_key)
        nonce = w3.eth.getTransactionCount(account.address, 'pending')
        
        # Build transaction
        contract_abi = [
            {
                "inputs": [
                    {"type": "address[]", "name": "recipients"},
                    {"type": "uint256[]", "name": "amounts"}
                ],
                "name": "withdraw",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        # Build transaction
        transaction = contract.functions.withdraw(recipients, amounts).buildTransaction({
            'nonce': nonce,
            'gas': 200000,  # Higher gas limit for contract interaction
            'gasPrice': w3.toWei('0.1', 'gwei'),
            'value': total_amount,
            'chainId': int(os.getenv('ETHEREUM_CHAIN_ID', 11155111))
        })
        
        # Sign and send transaction
        signed = Account.signTransaction(transaction, private_key)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        
        return jsonify({
            'success': True,
            'transaction_hash': w3.toHex(tx_hash),
            'message': 'Multi-withdrawal transaction submitted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
