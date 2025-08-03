#!/usr/bin/env python3
"""
Simple test script for Yaswanth's AI Twin
Run this to quickly test your AI twin without setup complexity
"""

import os
from ai_twin import YaswanthAITwin

def main():
    print("🤖 Yaswanth's AI Twin - Quick Test")
    print("=" * 40)
    
    # Get API key
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    try:
        # Initialize AI Twin
        print("\n🔄 Loading AI Twin...")
        ai_twin = YaswanthAITwin(api_key)
        
        # Load chat data
        print("📁 Loading chat data...")
        ai_twin.load_chat_data()
        
        print("\n✅ AI Twin Ready!")
        print("💡 Your personality has been loaded from personality.yaml")
        print("🎯 Type 'quit' to exit\n")
        
        # Simple chat loop
        while True:
            user_input = input("Indu: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Yaswanth: Sarsarle, catch you later! 😊")
                break
            
            if user_input:
                try:
                    response = ai_twin.generate_response(user_input)
                    print(f"Yaswanth: {response}\n")
                except Exception as e:
                    print(f"❌ Error: {e}\n")
    
    except Exception as e:
        print(f"❌ Failed to initialize AI Twin: {e}")
        print("💡 Make sure you've installed requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
