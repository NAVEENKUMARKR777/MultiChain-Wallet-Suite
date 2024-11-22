from mnemonic import Mnemonic
from eth_account import Account
from web3 import Web3
from bitcoin import *
import os
from typing import List, Tuple, Dict
import hashlib
import base58
import ecdsa
from eth_utils import to_checksum_address, remove_0x_prefix, to_bytes
from dotenv import load_dotenv

class MultiChainWallet:
    def __init__(self, mnemonic_phrase: str = None, testnet: bool = True):
        """Initialize wallet manager with optional mnemonic phrase"""
        # Load environment variables
        load_dotenv()
        
        self.mnemo = Mnemonic("english")
        self.mnemonic = mnemonic_phrase if mnemonic_phrase else self.mnemo.generate(strength=256)
        self.seed = self.mnemo.to_seed(self.mnemonic)
        self.testnet = testnet
        
        # Initialize Web3 for Ethereum
        ethereum_rpc = os.getenv('ETHEREUM_RPC_URL')
        if not ethereum_rpc:
            raise ValueError("ETHEREUM_RPC_URL not found in environment variables")
        self.w3 = Web3(Web3.HTTPProvider(ethereum_rpc))
        
        # Set network configurations
        self.eth_chain_id = int(os.getenv('ETHEREUM_CHAIN_ID', 5))  # Default to Goerli
        self.btc_network = os.getenv('BITCOIN_NETWORK', 'testnet')
        self.tron_network = os.getenv('TRON_NETWORK', 'nile')
    
    def _derive_private_key(self, account_index: int = 0, coin_type: int = 60) -> bytes:
        """Derive private key from seed using BIP44 path"""
        # Use Bitcoin's BIP32 implementation to derive the private key
        bip32_root = bip32_master_key(self.seed)
        # m/44'/coin_type'/0'/0/account_index
        bip32_child = bip32_ckd(bip32_root, 0x8000002C)  # 44'
        bip32_child = bip32_ckd(bip32_child, 0x80000000 | coin_type)  # coin_type'
        bip32_child = bip32_ckd(bip32_child, 0x80000000)  # 0'
        bip32_child = bip32_ckd(bip32_child, 0)          # 0
        bip32_child = bip32_ckd(bip32_child, account_index)
        
        # Get the raw private key bytes (removing the first byte which is the version)
        private_key = bip32_extract_key(bip32_child)
        return bytes.fromhex(private_key)[1:]  # Remove the first byte
    
    def generate_ethereum_wallet(self, account_index: int = 0) -> Dict[str, str]:
        """Generate Ethereum wallet from mnemonic"""
        private_key_bytes = self._derive_private_key(account_index, coin_type=60)
        private_key_hex = private_key_bytes.hex()
        acct = Account.privateKeyToAccount(private_key_bytes)
        
        return {
            'address': acct.address,
            'private_key': '0x' + private_key_hex,
            'network': 'goerli' if self.testnet else 'mainnet',
            'chain_id': self.eth_chain_id
        }
    
    def generate_bitcoin_wallet(self, account_index: int = 0) -> Dict[str, str]:
        """Generate Bitcoin wallet from mnemonic"""
        # Use coin_type 1 for testnet, 0 for mainnet
        coin_type = 1 if self.testnet else 0
        private_key_bytes = self._derive_private_key(account_index, coin_type=coin_type)
        private_key = private_key_bytes.hex()
        
        # Generate public key and address
        public_key = privtopub(private_key)
        if self.testnet:
            # Use testnet address version (0x6F)
            version = 111
        else:
            # Use mainnet address version (0x00)
            version = 0
            
        address = pubtoaddr(public_key, version)
        
        return {
            'address': address,
            'private_key': private_key,
            'network': self.btc_network
        }
    
    def generate_tron_wallet(self, account_index: int = 0) -> Dict[str, str]:
        """Generate Tron wallet from mnemonic"""
        private_key_bytes = self._derive_private_key(account_index, coin_type=195)
        private_key_hex = private_key_bytes.hex()
        
        # Generate public key
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        public_key = verifying_key.to_string()
        
        # Generate Tron address
        keccak = hashlib.sha3_256()
        keccak.update(public_key)
        keccak_digest = keccak.digest()
        
        # Take last 20 bytes and add prefix
        # Use 0xA0 for testnet and 0x41 for mainnet
        prefix = b'\xA0' if self.testnet else b'\x41'
        raw_addr = prefix + keccak_digest[-20:]
        
        # Add checksum
        h = hashlib.sha256()
        h.update(raw_addr)
        checksum = h.digest()
        h = hashlib.sha256()
        h.update(checksum)
        checksum = h.digest()
        
        # Encode address
        addr = raw_addr + checksum[:4]
        address = base58.b58encode(addr).decode('utf-8')
        
        return {
            'address': address,
            'private_key': '0x' + private_key_hex,
            'network': self.tron_network
        }
    
    def generate_all_wallets(self, account_index: int = 0) -> Dict[str, Dict[str, str]]:
        """Generate wallets for all supported chains"""
        return {
            'ethereum': self.generate_ethereum_wallet(account_index),
            'bitcoin': self.generate_bitcoin_wallet(account_index),
            'tron': self.generate_tron_wallet(account_index)
        }
    
    def validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address"""
        try:
            # Convert to checksum address and verify format
            checksum_address = to_checksum_address(address)
            return len(checksum_address) == 42 and checksum_address.startswith('0x')
        except:
            return False
    
    def validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address"""
        try:
            # Basic Bitcoin address validation
            if self.testnet:
                return address.startswith(('m', 'n', '2')) and len(address) > 26 and len(address) < 35
            return len(address) > 26 and len(address) < 35
        except:
            return False
    
    def validate_tron_address(self, address: str) -> bool:
        """Validate Tron address"""
        try:
            # Basic Tron address validation
            if self.testnet:
                return len(address) == 34  # Testnet addresses have same format
            return address.startswith('T') and len(address) == 34
        except:
            return False

    @staticmethod
    def get_mnemonic_words() -> List[str]:
        """Get list of valid mnemonic words"""
        return Mnemonic("english").wordlist
