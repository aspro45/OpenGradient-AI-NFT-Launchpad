import asyncio
from agent import chat_with_agent

async def async_main():
    print("=========================================")
    print("🚀 Welcome to the AI NFT Launchpad 🚀")
    print("Type 'exit' or 'quit' to leave.")
    print("=========================================")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                print("\nLaunchpad Agent: Goodbye! See you next mint! 👋")
                break
                
            if not user_input.strip():
                continue
                
            print("\nLaunchpad Agent is thinking...")
            print("Launchpad Agent: ", end="", flush=True)
            
            async for chunk in chat_with_agent(user_input, conversation_history):
                print(chunk, end="", flush=True)
            print()
            
        except KeyboardInterrupt:
            print("\nLaunchpad Agent: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n[Error connecting to agent]: {e}")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
