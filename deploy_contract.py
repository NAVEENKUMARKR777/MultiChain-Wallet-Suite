from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv

load_dotenv()

def deploy_multi_withdraw_contract(private_key: str, network_url: str) -> tuple:
    """
    Deploy the MultiWithdraw contract to the specified network
    
    Args:
        private_key (str): Private key of the deployer account
        network_url (str): URL of the Ethereum network (e.g., Infura endpoint)
        
    Returns:
        tuple: (contract_address, contract_abi)
    """
    # Initialize web3
    w3 = Web3(Web3.HTTPProvider(network_url))
    
    # Set up account
    account = Account.from_key(private_key)
    
    # Read contract source
    contract_path = os.path.join(os.path.dirname(__file__), 'contracts', 'MultiWithdraw.sol')
    
    # Compile contract (requires solc to be installed)
    from solcx import compile_source
    
    with open(contract_path, 'r') as file:
        contract_source = file.read()
    
    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin']
    )
    
    contract_id, contract_interface = compiled_sol.popitem()
    
    # Get contract binary and abi
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    
    # Create contract instance
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(account.address)
    transaction = Contract.constructor().build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    
    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt.contractAddress
    
    # Save contract ABI and address
    contract_data = {
        'address': contract_address,
        'abi': abi
    }
    
    with open('contract_data.json', 'w') as f:
        json.dump(contract_data, f, indent=4)
    
    return contract_address, abi

if __name__ == '__main__':
    # Load environment variables
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    NETWORK_URL = os.getenv('NETWORK_URL')
    
    if not PRIVATE_KEY or not NETWORK_URL:
        print("Please set PRIVATE_KEY and NETWORK_URL in .env file")
        exit(1)
    
    try:
        address, abi = deploy_multi_withdraw_contract(PRIVATE_KEY, NETWORK_URL)
        print(f"Contract deployed successfully at: {address}")
    except Exception as e:
        print(f"Error deploying contract: {str(e)}")
