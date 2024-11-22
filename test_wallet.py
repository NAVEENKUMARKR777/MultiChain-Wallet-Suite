from wallet_manager import MultiChainWallet
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize wallet manager with testnet=True
    wallet_manager = MultiChainWallet(testnet=True)
    
    # Display mnemonic phrase
    print("\nMnemonic phrase (SAVE THIS SECURELY):")
    print(wallet_manager.mnemonic)
    print("\n")
    
    # Generate wallets for all chains
    wallets = wallet_manager.generate_all_wallets()
    
    # Display wallet information
    for chain, wallet in wallets.items():
        print(f"\n{chain.upper()} Wallet ({wallet['network']}):")
        print(f"Address: {wallet['address']}")
        print(f"Private Key: {wallet['private_key']}")
        if chain == 'ethereum':
            print(f"Chain ID: {wallet['chain_id']}")
    
    # Validate addresses
    print("\nAddress Validation:")
    for chain, wallet in wallets.items():
        address = wallet['address']
        if chain == 'ethereum':
            is_valid = wallet_manager.validate_ethereum_address(address)
        elif chain == 'bitcoin':
            is_valid = wallet_manager.validate_bitcoin_address(address)
        else:  # tron
            is_valid = wallet_manager.validate_tron_address(address)
        print(f"{chain.capitalize()} address valid: {is_valid}")

if __name__ == "__main__":
    main()
