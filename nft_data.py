import json
import os

# Path for persisting user-deployed collections between serverless invocations
_DB_PATH = "/tmp/collections_db.json"

# Hardcoded base collections — these are always available
_BASE_COLLECTIONS = {
    "ASPRO": {
        "price_eth": 0.0,
        "gas_estimate_eth": 0.005,
        "is_free_mint": True,
        "supply": "unlimited",
        "contract_address": "0x064776eA68Cd90d62e85e5a8151b63EfcB16F029",
        "description": "Exclusive free mint for early launchpad testers. Unlimited supply!"
    },
    "CyberPunks": {
        "price_eth": 0.1,
        "gas_estimate_eth": 0.005,
        "is_free_mint": False,
        "supply": "10000",
        "contract_address": "0xMockCyberPunksContractAddress",
        "description": "A popular premium profile picture collection."
    }
}

def _load_db() -> dict:
    """Load user-deployed collections from persistent storage."""
    try:
        if os.path.exists(_DB_PATH):
            with open(_DB_PATH, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_db(user_collections: dict):
    """Save user-deployed collections to persistent storage."""
    try:
        with open(_DB_PATH, "w") as f:
            json.dump(user_collections, f, indent=2)
    except Exception:
        pass

# Build the live registry: base collections + any previously deployed ones
NFT_COLLECTIONS = {**_BASE_COLLECTIONS, **_load_db()}


def get_collection_info(collection_name: str) -> str:
    """Returns details about a specific NFT collection as a JSON string for the AI."""
    # Always reload from disk to catch collections deployed in other sessions
    live = {**_BASE_COLLECTIONS, **_load_db()}
    name_key = collection_name.strip()

    for key, data in live.items():
        if key.lower() == name_key.lower():
            return json.dumps({"name": key, **data})

    return json.dumps({"error": f"Collection '{collection_name}' not found on this launchpad."})


def register_new_collection(collection_name: str, symbol: str, price_eth: float, supply: int, description: str) -> str:
    """Deploys a real ERC721 NFT collection smart contract and registers it on the Launchpad."""
    from blockchain_utils import deploy_nft_contract

    name_key = collection_name.strip()

    # Reload latest state before checking for duplicates
    user_collections = _load_db()
    all_collections = {**_BASE_COLLECTIONS, **user_collections}

    for key in all_collections.keys():
        if key.lower() == name_key.lower():
            return json.dumps({"error": f"Collection '{collection_name}' already exists on this launchpad!"})

    # Deploy the real smart contract
    result_json = deploy_nft_contract(collection_name=name_key, symbol=symbol.strip().upper())
    result = json.loads(result_json)

    if result.get("status") != "success":
        return json.dumps({"error": f"Smart contract deployment failed: {result.get('message', 'Unknown error')}"})

    real_address = result["contract_address"]
    deploy_tx = result["deploy_tx"]

    new_entry = {
        "price_eth": float(price_eth),
        "gas_estimate_eth": 0.005,
        "is_free_mint": float(price_eth) == 0.0,
        "supply": str(supply) if supply > 0 else "unlimited",
        "contract_address": real_address,
        "description": description
    }

    # Persist to disk so the collection survives across sessions
    user_collections[name_key] = new_entry
    _save_db(user_collections)

    # Update in-memory dict too
    NFT_COLLECTIONS[name_key] = new_entry

    return json.dumps({
        "success": True,
        "message": f"🚀 Collection '{name_key}' ({symbol.upper()}) has been successfully deployed to Base Sepolia!",
        "contract_address": real_address,
        "deploy_tx_hash": deploy_tx,
        "basescan_url": f"https://sepolia.basescan.org/address/{real_address}"
    })
