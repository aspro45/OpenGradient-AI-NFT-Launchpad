import time
import os
import json
from web3 import Web3

# Using Base Sepolia for realistic testing of receipts
w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))

AGENT_WALLET = "0x32e75870fB68372d703ED6867cF6A1E52C4769EE"

# Fee charged to deploy a new custom NFT collection to the Launchpad
DEPLOYMENT_FEE_ETH = 0.01

def deploy_nft_contract(collection_name: str, symbol: str) -> str:
    """
    Deploys a real ERC721 smart contract to Base Sepolia for a new collection.
    Returns the deployed contract address, or an error message.
    """
    try:
        private_key = os.environ.get("AGENT_PRIVATE_KEY")
        if not private_key:
            return json.dumps({"status": "error", "message": "Server configuration error: AGENT_PRIVATE_KEY is missing."})

        # Load the precompiled contract artifact (no solcx needed at runtime)
        artifact_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "contract_artifact.json")
        with open(artifact_path, "r") as f:
            artifact = json.load(f)

        bytecode = artifact["bytecode"]
        abi = artifact["abi"]

        account = w3.eth.account.from_key(private_key)
        Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(account.address)

        # Build the deployment transaction with name & symbol constructor args
        built_tx = Contract.constructor(collection_name, symbol).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "maxFeePerGas": w3.eth.max_priority_fee + (2 * w3.eth.get_block("pending")["baseFeePerGas"]),
            "maxPriorityFeePerGas": w3.eth.max_priority_fee,
        })

        signed_tx = w3.eth.account.sign_transaction(built_tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for the mining receipt to get the real contract address
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        contract_address = receipt.contractAddress

        return json.dumps({
            "status": "success",
            "contract_address": contract_address,
            "deploy_tx": w3.to_hex(tx_hash)
        })

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def verify_payment_transaction(tx_hash: str, expected_amount_eth: float) -> str:
    """
    Checks if a transaction successfully sent the expected amount of ETH to the Agent Wallet.
    """
    if not w3.is_connected():
        return "Failed to connect to the blockchain RPC."
        
    try:
        # Wait a moment as blockchains take time (mocking reality)
        time.sleep(1) 
        
        tx = w3.eth.get_transaction(tx_hash)
        
        # Verify the recipient
        if tx.to.lower() != AGENT_WALLET.lower():
            return f"Verification Failed: Transaction was sent to {tx.to}, not the launchpad address ({AGENT_WALLET})."
            
        # Verify the amount
        actual_eth = float(w3.from_wei(tx.value, 'ether'))
        if actual_eth < expected_amount_eth:
             return f"Verification Failed: Insufficient funds sent. Expected {expected_amount_eth} ETH, but received {actual_eth} ETH."
             
        # Verify it was successful 
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt.status != 1:
            return "Verification Failed: The transaction failed on-chain or is still pending."
            
        return "Verification Successful: Payment confirmed!"

    except Exception as e:
        return f"Error verifying transaction: {str(e)}"

from nft_data import get_collection_info

def execute_mint_nft(user_address: str, collection_name: str) -> str:
    """
    Executes a real smart contract mint function on the Base Sepolia testnet.
    """
    info_json = get_collection_info(collection_name)
    info = json.loads(info_json)
    
    contract_address = info.get("contract_address")
    
    if not contract_address or contract_address.startswith("0xMock"):
        return json.dumps({
            "status": "error",
            "message": f"No real contract deployed for {collection_name}."
        })
        
    try:
        import os
        abi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aspro_abi.json")
        with open(abi_path, "r") as f:
            abi = json.load(f)
            
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Agent's private key to sponsor the mint transaction
        private_key = os.environ.get("AGENT_PRIVATE_KEY")
        if not private_key:
            return json.dumps({
                "status": "error",
                "message": "Server configuration error: AGENT_PRIVATE_KEY is missing."
            })
        account = w3.eth.account.from_key(private_key)
        
        nonce = w3.eth.get_transaction_count(account.address)
        
        checksum_address = w3.to_checksum_address(user_address)
        
        # Build the Mint Transaction
        built_tx = contract.functions.mint(checksum_address).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'maxFeePerGas': w3.eth.max_priority_fee + (2 * w3.eth.get_block('pending')['baseFeePerGas']),
            'maxPriorityFeePerGas': w3.eth.max_priority_fee,
        })
        
        signed_tx = w3.eth.account.sign_transaction(built_tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully minted 1 {collection_name} NFT to {user_address}!",
            "mint_transaction_hash": w3.to_hex(tx_hash)
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
