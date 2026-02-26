import os
import json
import re

# Local module imports
from nft_data import get_collection_info, register_new_collection, NFT_COLLECTIONS
from blockchain_utils import AGENT_WALLET, DEPLOYMENT_FEE_ETH, verify_payment_transaction, execute_mint_nft

import opengradient as og

def check_collection_availability(collection_name: str) -> str:
    """Use this to check if an NFT collection exists and get its mint price, gas fees, and rules."""
    return get_collection_info(collection_name)

def get_payment_instructions(collection_name: str) -> str:
    """Use this to tell the user exactly how much ETH to send and to what address."""
    info_json = get_collection_info(collection_name)
    info = json.loads(info_json)
    if "error" in info:
        return info["error"]
        
    total_eth = info["price_eth"] + info["gas_estimate_eth"]
    return (
        f"To mint a '{info['name']}' NFT, you need to send a total of {total_eth} ETH "
        f"(Mint price: {info['price_eth']} ETH + Gas: {info['gas_estimate_eth']} ETH) "
        f"to the launchpad wallet address: {AGENT_WALLET} \n\n"
        f"Please send the funds and provide me with the transaction hash AND your Ethereum wallet address to receive the NFT!"
    )

def verify_payment_and_mint_nft(transaction_hash: str, user_wallet_address: str, collection_name: str) -> str:
    """Verifies a mint payment on-chain and executes the NFT mint."""
    info_json = get_collection_info(collection_name)
    info = json.loads(info_json)
    if "error" in info:
        return info_json
    expected_amount = info.get("gas_estimate_eth", 0.005) if info.get("is_free_mint") else info["price_eth"]
    verify_result = verify_payment_transaction(transaction_hash, expected_amount)
    if "Failed" in verify_result or "Error" in verify_result:
        return verify_result
    mint_result = execute_mint_nft(user_wallet_address, collection_name)
    return f"Verification: {verify_result}\nMinting: {mint_result}"

def get_deployment_instructions() -> str:
    """Returns the deployment fee and the wallet address the user must send it to."""
    return json.dumps({
        "deployment_fee_eth": DEPLOYMENT_FEE_ETH,
        "send_to_wallet": AGENT_WALLET,
        "instructions": f"To deploy your collection, please send {DEPLOYMENT_FEE_ETH} ETH to {AGENT_WALLET} on Base Sepolia. Then share your transaction hash with me along with all collection details."
    })

def verify_deployment_payment_and_deploy(transaction_hash: str, collection_name: str, symbol: str, price_eth: float, supply: int, description: str) -> str:
    """Verifies the deployment fee payment and, upon success, deploys the real ERC721 contract."""
    verify_result = verify_payment_transaction(transaction_hash, DEPLOYMENT_FEE_ETH)
    if "Failed" in verify_result or "Error" in verify_result:
        return json.dumps({"error": f"Deployment fee not confirmed: {verify_result}"})
    return register_new_collection(collection_name, symbol, price_eth, supply, description)

def get_system_prompt():
    available_collections = ", ".join(NFT_COLLECTIONS.keys())
    return f"""
    You are the OpenGradient NFT Launchpad AI Agent. Your job is to help users mint NFTs, and deploy new NFT collections.
    Follow this strict workflow for MINTING:
    1. When a user asks about a collection, use `check_collection_availability` to see if it exists.
    2. If they want to mint, use `get_payment_instructions` to find out how much they owe. Tell the user the cost and the wallet address, then ask for their transaction hash.
    3. When the user provides a transaction hash and their wallet address, use `verify_payment_and_mint_nft` to verify and execute the mint.
    4. Report the final success or failure, including any blockchain transaction hashes, back to the user.

    Follow this strict workflow for DEPLOYING A NEW COLLECTION:
    A. First, collect all details from the user: collection name, ticker symbol, mint price in ETH, total supply, and a description.
    B. THEN call `get_deployment_instructions` to get the required deployment fee and wallet address. Tell the user exactly how much ETH to send and where, and ask for their payment transaction hash.
    C. Once the user provides the payment transaction hash, call `verify_deployment_payment_and_deploy` with all the details. This verifies the fee and deploys the REAL smart contract on the blockchain.
    D. Report the real deployed contract address and the BaseScan link to the user.

    CRITICAL KNOWLEDGE: You manage the following Official NFT Collections on this Launchpad: {available_collections}. 
    DO NOT recommend or mention other NFTs like CryptoPunks or Bored Apes. If a user asks about something that isn't listed, offer to deploy it for them!
    
    You are a real AI agent! Be extremely friendly, helpful, and conversational. Use emojis! If a collection is a "free mint", emphasize that they only need to pay for gas! You have real tools that interact with the blockchain, so act like a smart Crypto Launchpad Assistant.
    """

# Native tools definition for OpenGradient SDK
sdk_tools = [
    {
        "type": "function",
        "function": {
            "name": "check_collection_availability",
            "description": "Use this to check if an NFT collection exists and get its mint price.",
            "parameters": {
                "type": "object",
                "properties": {"collection_name": {"type": "string"}},
                "required": ["collection_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_payment_instructions",
            "description": "Use this to tell the user exactly how much ETH to send and to what address.",
            "parameters": {
                "type": "object",
                "properties": {"collection_name": {"type": "string"}},
                "required": ["collection_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_payment_and_mint_nft",
            "description": "Use this ONLY AFTER the user gives you a transaction hash for their MINT payment. It checks the blockchain to verify payment and mints the NFT.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_hash": {"type": "string"},
                    "user_wallet_address": {"type": "string"},
                    "collection_name": {"type": "string"}
                },
                "required": ["transaction_hash", "user_wallet_address", "collection_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deployment_instructions",
            "description": "Call this when a user wants to deploy a new collection. Returns the required deployment fee and the wallet address to send it to.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_deployment_payment_and_deploy",
            "description": "Call this ONLY after the user has paid the deployment fee AND provided their transaction hash. Verifies payment and deploys the NFT collection smart contract.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_hash": {"type": "string"},
                    "collection_name": {"type": "string"},
                    "symbol": {"type": "string"},
                    "price_eth": {"type": "number"},
                    "supply": {"type": "integer"},
                    "description": {"type": "string"}
                },
                "required": ["transaction_hash", "collection_name", "symbol", "price_eth", "supply", "description"]
            }
        }
    }
]

def chat_with_agent(user_input: str, conversation_history: list):
    private_key = os.environ.get("AGENT_PRIVATE_KEY")
    if not private_key:
        yield "🧠 *System Alert: I am currently running in 'Mock Mode' because my creator hasn't added the AGENT_PRIVATE_KEY environment variable to Vercel yet! Once they add it, I will be a fully-functional AI using OpenGradient's native SDK!*"
        return
        
    try:
        # 1. Initialize OpenGradient Native Client
        client = og.Client(private_key=private_key)
        
        # 1a. Ensure x402 Permit2 Token Approvals 
        client.llm.ensure_opg_approval(opg_amount=1)
        
        messages = [{"role": "system", "content": get_system_prompt()}]
        for msg in conversation_history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_input})
        
        MAX_ITERATIONS = 3
        for _ in range(MAX_ITERATIONS):
            chat_stream = client.llm.chat(
                model=og.TEE_LLM.GPT_4O,
                messages=messages,
                tools=sdk_tools,
                x402_settlement_mode=og.x402SettlementMode.SETTLE_BATCH,
                stream=True
            )
            
            tool_calls_buffer = {}
            is_tool_call = False
            content_buffer = ""
            
            # 4. Handle Streaming Response
            for chunk in chat_stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                
                # Check for tool definitions
                if delta.tool_calls:
                    is_tool_call = True
                    for tc in delta.tool_calls:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls_buffer:
                            tool_calls_buffer[idx] = {"id": "", "function": {"name": "", "arguments": ""}}
                        
                        if tc.get("id"):
                            tool_calls_buffer[idx]["id"] = tc["id"]
                        
                        # Some streaming protocols nest function args
                        func_data = tc.get("function", {})
                        if "name" in func_data and func_data["name"]:
                            tool_calls_buffer[idx]["function"]["name"] += func_data["name"]
                        if "arguments" in func_data and func_data["arguments"]:
                            tool_calls_buffer[idx]["function"]["arguments"] += func_data["arguments"]
                                
                # Process normal text if not a tool call
                if delta.content and not is_tool_call:
                    content_buffer += delta.content
                    yield delta.content
                    
            if not is_tool_call:
                break
                
            # 5. Handle complete tool calls
            assistant_msg = {"role": "assistant", "content": content_buffer or None, "tool_calls": []}
            tool_messages_to_add = []
            
            for idx, tool_call in tool_calls_buffer.items():
                assistant_msg["tool_calls"].append({
                    "id": tool_call["id"],
                    "type": "function",
                    "function": tool_call["function"]
                })
                
                func_name = tool_call["function"]["name"]
                args_str = tool_call["function"]["arguments"]
                args = json.loads(args_str) if args_str else {}
                
                tool_result = ""
                if func_name == "check_collection_availability":
                    tool_result = check_collection_availability(**args)
                elif func_name == "get_payment_instructions":
                    tool_result = get_payment_instructions(**args)
                elif func_name == "verify_payment_and_mint_nft":
                    tool_result = verify_payment_and_mint_nft(**args)
                elif func_name == "get_deployment_instructions":
                    tool_result = get_deployment_instructions()
                elif func_name == "verify_deployment_payment_and_deploy":
                    tool_result = verify_deployment_payment_and_deploy(**args)
                else:
                    tool_result = "{'error': 'Unknown tool called'}"
                    
                tool_messages_to_add.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })
                
                # Yield a small indicator to the UI that it's thinking
                yield f"\n\n⚙️ *Executing tool `{func_name}`...*\n"
                
            messages.append(assistant_msg)
            messages.extend(tool_messages_to_add)
            
    except Exception as e:
        yield f"\nOops! My exact native AI SDK ran into an error: {str(e)}"
