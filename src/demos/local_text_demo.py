"""
Local text demo for testing Gemini text generation.
Simple CLI loop to chat with Gemini AI.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.gemini_client import get_gemini_client


async def main():
    """Run interactive text chat demo."""
    print("=" * 60)
    print("🤖 AI Calling Agent - Text Chat Demo")
    print("=" * 60)
    print("Chat with Gemini AI. Type 'exit' or 'quit' to stop.\n")
    
    # Initialize client
    try:
        client = get_gemini_client()
        print(f"✅ Connected to Gemini ({client.text_model})\n")
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return
    
    # Conversation history
    history = []
    
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Generate response
        try:
            print("AI: ", end="", flush=True)
            
            # Use streaming for better UX
            response_text = ""
            async for chunk in client.stream_text(
                message=user_input,
                history=history
            ):
                print(chunk, end="", flush=True)
                response_text += chunk
            
            print("\n")
            
            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "model", "content": response_text})
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
