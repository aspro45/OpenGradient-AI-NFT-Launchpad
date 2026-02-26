import sys
from agent import chat_with_agent

def main():
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
            response = chat_with_agent(user_input, conversation_history)
            
            print(f"\nLaunchpad Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nLaunchpad Agent: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n[Error connecting to agent]: {e}")

if __name__ == "__main__":
    main()
