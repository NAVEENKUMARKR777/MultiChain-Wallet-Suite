# MultiChain Wallet Suite

A comprehensive wallet management system that supports Ethereum, Bitcoin, and Tron networks, with a smart contract for multi-address withdrawals.

## Features

- Generate wallets for multiple chains (ETH, BTC, TRON) from a single mnemonic seed
- Validate wallet addresses across different chains
- Smart contract for executing multi-address withdrawals in a single transaction
- Secure wallet generation following BIP44 standards
- Support for deterministic wallet generation

## Prerequisites

- Python 3.8+
- Solidity compiler (solc)
- Node.js and npm (for contract deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MultiChain-Wallet-Suite
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```env
PRIVATE_KEY=your_ethereum_private_key
NETWORK_URL=your_ethereum_network_url  # e.g., Infura endpoint
```

## Usage

### Generating Wallets

```python
from wallet_manager import MultiChainWallet

# Initialize wallet manager with optional mnemonic
wallet_manager = MultiChainWallet()

# Generate wallets for all chains
wallets = wallet_manager.generate_all_wallets()

# Access individual wallet addresses and private keys
eth_wallet = wallets['ethereum']
btc_wallet = wallets['bitcoin']
tron_wallet = wallets['tron']

print(f"Ethereum Address: {eth_wallet['address']}")
print(f"Bitcoin Address: {btc_wallet['address']}")
print(f"Tron Address: {tron_wallet['address']}")
```

### Deploying the MultiWithdraw Contract

1. Make sure you have set up your `.env` file with the required variables.

2. Run the deployment script:
```bash
python deploy_contract.py
```

The script will:
- Compile the MultiWithdraw contract
- Deploy it to the specified network
- Save the contract address and ABI to `contract_data.json`

## Smart Contract Usage

The MultiWithdraw contract allows you to send ETH to multiple addresses in a single transaction:

1. Call the `withdraw` function with arrays of recipient addresses and corresponding amounts
2. The contract will distribute the ETH according to the specified amounts
3. Any excess ETH sent will be refunded to the sender

## Security Considerations

- Keep your mnemonic phrase and private keys secure
- Never share your private keys or store them in plain text
- Use environment variables for sensitive data
- Consider using a hardware wallet for production deployments

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
