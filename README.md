# MultiChain Wallet Suite

A comprehensive multi-blockchain wallet management system with advanced smart contract interaction capabilities. Currently supports Ethereum (Sepolia Testnet), Bitcoin (Testnet), and Tron (Nile Testnet).

## Features

- 🔐 **Secure Wallet Generation**
  - BIP44 compliant HD wallet generation
  - Support for multiple blockchain networks
  - Optional mnemonic phrase import

- 💸 **Transaction Management**
  - Send and receive transactions
  - Real-time balance checking
  - Gas price optimization
  - Transaction status tracking

- 📝 **Smart Contract Integration**
  - MultiWithdraw contract support
  - Batch transaction processing
  - Contract deployment tracking
  - Interactive contract interface

- 🛡️ **Security Features**
  - Client-side and server-side validation
  - Secure key management
  - Testnet-focused development
  - Error message obfuscation

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for frontend development)
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multichain-wallet-suite.git
   cd multichain-wallet-suite
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```env
   # Ethereum (Sepolia Testnet)
   ETHEREUM_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/{your project ID}
   ETHEREUM_NETWORK=sepolia
   ETHEREUM_CHAIN_ID=11155111

   # Bitcoin (Testnet)
   BITCOIN_NETWORK=testnet

   # Tron (Nile Testnet)
   TRON_NETWORK=nile
   TRON_RPC_URL=https://nile.trongrid.io

   # Contract Deployment
   DEPLOYER_PRIVATE_KEY=your_private_key_here

   # Gas Settings (optional)
   GAS_PRICE_GWEI=0.1
   GAS_LIMIT=21000
   ```

## Configuration

1. **Ethereum Setup**:
   - Create an account on [Alchemy](https://www.alchemy.com/)
   - Create a new app for Sepolia testnet
   - Copy the API key to `ETHEREUM_RPC_URL` in `.env`

2. **Bitcoin Setup**:
   - No additional setup needed for testnet
   - Uses public Bitcoin testnet nodes

3. **Tron Setup**:
   - Register on [TRON Grid](https://www.trongrid.io/)
   - Use Nile testnet for development

4. **Contract Deployment**:
   - Generate a deployer wallet
   - Fund it with testnet ETH
   - Add private key to `DEPLOYER_PRIVATE_KEY` in `.env`

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Access the application:
   - Open `http://localhost:5000` in your browser
   - Make sure you're connected to the internet

## Usage Guide

### Wallet Generation
1. Click "Generate Wallets"
2. Save the mnemonic phrase securely
3. Access your generated wallets

### Sending Transactions
1. Select the blockchain network
2. Enter recipient address
3. Specify amount
4. Sign with private key
5. Confirm transaction

### Using MultiWithdraw Contract
1. Navigate to Contracts section
2. Click "Use Contract" on MultiWithdraw
3. Add recipient addresses and amounts
4. Sign with your private key
5. Submit the transaction

## Development

### Project Structure
```
multichain-wallet-suite/
├── app.py              # Flask application
├── wallet_manager.py   # Wallet management logic
├── requirements.txt    # Python dependencies
├── static/
│   └── js/
│       └── main.js    # Frontend JavaScript
├── templates/
│   └── index.html     # Main UI template
└── contracts/
    └── deployed_contracts.json  # Contract tracking
```

### Adding New Features
1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Submit pull request

## Testing

1. Run unit tests:
   ```bash
   python -m pytest tests/
   ```

2. Test on testnets before mainnet deployment

## Security Considerations

- Never share private keys
- Use environment variables for sensitive data
- Always validate input data
- Keep dependencies updated
- Use testnet for development

## Troubleshooting

### Common Issues

1. **Transaction Fails**
   - Check network connection
   - Verify sufficient balance
   - Confirm gas settings

2. **Contract Interaction Fails**
   - Verify contract address
   - Check transaction parameters
   - Ensure sufficient gas

3. **Wallet Generation Issues**
   - Verify mnemonic format
   - Check network connectivity
   - Confirm environment variables

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check documentation
2. Search existing issues
3. Create new issue if needed

## Acknowledgments

- Web3.py team
- Flask community
- Blockchain testnet providers
