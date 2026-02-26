import os
from solcx import compile_source, install_solc
from web3 import Web3
import json

def deploy():
    # Attempt to install solc if missing
    try:
        install_solc("0.8.20")
    except Exception:
        pass

    with open("AsproLaunchpad.sol", "r") as f:
        contract_source = f.read()

    print("Compiling contract...")
    compiled = compile_source(contract_source, solc_version="0.8.20")
    contract_id, contract_interface = compiled.popitem()

    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    print("Connecting to Base Sepolia...")
    w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
    print(f"Connected: {w3.is_connected()}")

    # Use the test agent wallet private key we used previously
    private_key = os.environ.get("AGENT_PRIVATE_KEY")
    if not private_key:
        print("Error: AGENT_PRIVATE_KEY environment variable is not set.")
        return
    account = w3.eth.account.from_key(private_key)
    print(f"Deploying from wallet: {account.address}")
    
    balance = w3.eth.get_balance(account.address)
    print(f"Wallet Balance: {w3.from_wei(balance, 'ether')} ETH")

    AsproContract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(account.address)
    
    # Estimate gas
    construct_txn = AsproContract.constructor().build_transaction({
        'from': account.address,
        'nonce': nonce,
    })
    
    gas_estimate = w3.eth.estimate_gas(construct_txn)
    gas_price_multiplier = 1.1 # 10% buffer
    
    built_tx = AsproContract.constructor().build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': int(gas_estimate * gas_price_multiplier),
        'maxFeePerGas': w3.eth.max_priority_fee + (2 * w3.eth.get_block('pending')['baseFeePerGas']),
        'maxPriorityFeePerGas': w3.eth.max_priority_fee,
    })

    print("Signing transaction...")
    signed_tx = w3.eth.account.sign_transaction(built_tx, private_key=private_key)

    print("Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction hash: {w3.to_hex(tx_hash)}")

    print("Waiting for receipt...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed successfully at: {contract_address}")
    
    # Save the ABI for the agent to use
    with open("aspro_abi.json", "w") as f:
        json.dump(abi, f)

if __name__ == "__main__":
    deploy()
