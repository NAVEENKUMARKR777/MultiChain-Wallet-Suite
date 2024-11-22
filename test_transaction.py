from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Connect to Sepolia network
    w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL')))
    
    # Simple connection test
    try:
        w3.eth.blockNumber
        print(f"Connected to network: {os.getenv('ETHEREUM_NETWORK')}")
    except Exception as e:
        raise Exception(f"Failed to connect to Ethereum network: {str(e)}")
    
    # Get deployer account
    deployer_private_key = os.getenv('DEPLOYER_PRIVATE_KEY')
    if not deployer_private_key.startswith('0x'):
        deployer_private_key = '0x' + deployer_private_key
    
    account = Account.from_key(deployer_private_key)
    print(f"\nFrom Address: {account.address}")
    
    # Get account balance
    balance = w3.eth.getBalance(account.address)
    balance_eth = w3.fromWei(balance, 'ether')
    print(f"Balance: {balance_eth} ETH")
    
    # Create transaction
    # We'll send a small amount to a test address
    recipient = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Example test address
    value = w3.toWei(0.0001, 'ether')
    
    # Get nonce
    nonce = w3.eth.getTransactionCount(account.address)
    
    # Get gas price from .env, convert to Wei
    gas_price_gwei = float(os.getenv('GAS_PRICE_GWEI', '0.1'))
    gas_price = w3.toWei(gas_price_gwei, 'gwei')
    
    # Get gas limit from .env
    gas_limit = int(os.getenv('GAS_LIMIT', '15000'))
    
    # Build transaction
    transaction = {
        'nonce': nonce,
        'to': recipient,
        'value': value,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': int(os.getenv('ETHEREUM_CHAIN_ID', 11155111))
    }
    
    # Show transaction details before sending
    print("\nTransaction Details:")
    print(f"To: {recipient}")
    print(f"Value: {w3.fromWei(value, 'ether')} ETH")
    print(f"Gas Price: {gas_price_gwei} Gwei")
    print(f"Gas Limit: {gas_limit}")
    print(f"Total Cost (max): {w3.fromWei(value + (gas_price * gas_limit), 'ether')} ETH")
    
    # Sign transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, deployer_private_key)
    
    # Send transaction
    print("\nSending transaction...")
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    # Wait for transaction receipt
    print("\nWaiting for transaction confirmation...")
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(f"Transaction confirmed in block {tx_receipt['blockNumber']}")
    print(f"Gas used: {tx_receipt['gasUsed']}")
    print(f"Actual transaction cost: {w3.fromWei(tx_receipt['gasUsed'] * gas_price, 'ether')} ETH")
    
    # Get new balance
    new_balance = w3.eth.getBalance(account.address)
    print(f"\nNew balance: {w3.fromWei(new_balance, 'ether')} ETH")
    print(f"Total ETH spent: {w3.fromWei(balance - new_balance, 'ether')} ETH")

if __name__ == "__main__":
    main()
