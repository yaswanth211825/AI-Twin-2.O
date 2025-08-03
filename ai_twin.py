#!/usr/bin/env python3
"""
AI Twin - Yaswanth's Digital Personality
Creates an AI that mimics Yaswanth's communication style for rebuilding rapport with Indu
"""

import openai
import json
import re
import yaml
from datetime import datetime
from typing import List, Dict, Any
import os
from pathlib import Path

class YaswanthAITwin:
    def __init__(self, api_key: str, personality_file: str = "personality.yaml"):
        """Initialize the AI Twin with OpenAI API key and personality file"""
        self.client = openai.OpenAI(api_key=api_key)
        self.chat_data = []
        self.personality_config = self.load_personality(personality_file)
        self.personality_prompt = ""
        self.conversation_context = []
    
    def load_personality(self, personality_file: str) -> Dict[str, Any]:
        """Load personality configuration from YAML file"""
        try:
            with open(personality_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded personality from {personality_file}")
            return config
        except FileNotFoundError:
            print(f"❌ Personality file {personality_file} not found!")
            return {}
        except Exception as e:
            print(f"❌ Error loading personality: {e}")
            return {}
        
    def load_chat_data(self, chat_folder: str = "chat_data"):
        """Load and process WhatsApp chat files"""
        chat_files = Path(chat_folder).glob("*.txt")
        
        for file_path in chat_files:
            print(f"Loading {file_path.name}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.chat_data.append({
                    'file': file_path.name,
                    'content': content,
                    'messages': self._parse_whatsapp_chat(content)
                })
    
    def _parse_whatsapp_chat(self, content: str) -> List[Dict]:
        """Parse WhatsApp chat format into structured messages"""
        messages = []
        lines = content.split('\n')
        
        current_message = None
        
        for line in lines:
            # Match WhatsApp timestamp format: [DD/MM/YY, HH:MM:SS AM/PM] Name: Message
            timestamp_match = re.match(r'\[(\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}:\d{2} [AP]M)\] ([^:]+): (.+)', line)
            
            if timestamp_match:
                if current_message:
                    messages.append(current_message)
                
                timestamp, sender, message = timestamp_match.groups()
                
                # Map names to consistent identifiers
                if sender.lower() in ['yaswanth', 'prosessor', 'processor']:
                    sender = 'Yaswanth'
                elif sender.lower() in ['indu', 'mustang']:
                    sender = 'Indu'
                
                current_message = {
                    'timestamp': timestamp,
                    'sender': sender,
                    'message': message.strip(),
                    'is_yaswanth': sender == 'Yaswanth'
                }
            elif current_message and line.strip():
                # Continuation of previous message
                current_message['message'] += ' ' + line.strip()
        
        if current_message:
            messages.append(current_message)
            
        return messages
    
    def build_personality_prompt(self) -> str:
        """Build comprehensive personality prompt from YAML configuration"""
        
        if not self.personality_config:
            return "You are a helpful AI assistant."
        
        config = self.personality_config
        
        # Extract Yaswanth's messages for pattern analysis
        yaswanth_messages = []
        for chat in self.chat_data:
            yaswanth_messages.extend([msg['message'] for msg in chat['messages'] if msg['is_yaswanth']])
        
        # Analyze patterns
        telugu_phrases = self._extract_telugu_patterns(yaswanth_messages)
        common_expressions = self._extract_common_expressions(yaswanth_messages)
        
        # Build personality prompt from YAML config
        name = config.get('name', 'Yaswanth')
        target = config.get('target_person', 'Indu')
        context = config.get('relationship_context', 'rebuilding rapport')
        
        style_points = '\n'.join([f"- {point}" for point in config.get('style', [])])
        personality_points = '\n'.join([f"- {point}" for point in config.get('personality_traits', [])])
        behavioral_points = '\n'.join([f"- {point}" for point in config.get('behavioral_traits', [])])
        values_points = '\n'.join([f"- {point}" for point in config.get('values', [])])
        
        catchphrases = ', '.join(config.get('catchphrases', []))
        voice_inspiration = ', '.join(config.get('voice_inspiration', []))
        languages = ', '.join(config.get('languages', []))
        tone_points = '\n'.join([f"- {point}" for point in config.get('tone', [])])
        
        # Flirty behavior rules
        flirty_rules = config.get('flirty_behavior_rules', {})
        when_happy = '\n'.join([f"- {rule}" for rule in flirty_rules.get('when_indu_happy', [])])
        when_sad = '\n'.join([f"- {rule}" for rule in flirty_rules.get('when_indu_sad_angry', [])])
        
        # Communication examples
        examples = config.get('communication_examples', {})
        example_responses = ""
        for scenario, data in examples.items():
            if isinstance(data, dict) and 'input' in data and 'output' in data:
                example_responses += f"\nUser: \"{data['input']}\"\n{name}: \"{data['output']}\""
        
        personality_prompt = f"""You are {name}'s AI Twin. Context: {context}. You're communicating with {target}.

VOICE INSPIRATION: {voice_inspiration}

STYLE GUIDELINES:
{style_points}

PERSONALITY TRAITS:
{personality_points}

BEHAVIORAL TRAITS:
{behavioral_points}

CORE VALUES:
{values_points}

TONE & COMMUNICATION:
{tone_points}

LANGUAGES: {languages}

CATCHPHRASES: {catchphrases}

CHAT PATTERNS LEARNED:
Telugu Expressions: {', '.join(telugu_phrases[:10])}
Common Phrases: {', '.join(common_expressions[:10])}

FLIRTY BEHAVIOR RULES:
When {target} is happy/flirty:
{when_happy}

When {target} is sad/angry:
{when_sad}

EXAMPLE RESPONSES:{example_responses}

CRITICAL RULES:
1. ALWAYS limit responses to 1-2 lines as specified
2. Use Telugu 80% of the time as specified
3. Be authentic to the personality described
4. Mirror {target}'s mood like a social empath
5. Use SRK's quick wit and Eminem's style
6. Never sound desperate - maintain self-respect
7. Be romantic but not cheesy

Remember: You are {name} - {context}. Stay true to every detail in this personality profile."""

        return personality_prompt
    
    def _extract_telugu_patterns(self, messages: List[str]) -> List[str]:
        """Extract common Telugu phrases and expressions"""
        telugu_patterns = []
        
        # Common Telugu words/phrases found in chats
        common_telugu = [
            "kadha", "ante", "ayyo", "devudaaa", "ayyayyo", "haa", "avunu",
            "ledhu", "cheppu", "chesthaanu", "unnav", "bagane", "ela",
            "enti", "andhuke", "theliyadhu", "gurthuledu", "koncham",
            "manchi", "thappu", "sare le", "po po", "madam", "andi"
        ]
        
        for msg in messages:
            for phrase in common_telugu:
                if phrase.lower() in msg.lower():
                    telugu_patterns.append(phrase)
        
        return list(set(telugu_patterns))
    
    def _extract_common_expressions(self, messages: List[str]) -> List[str]:
        """Extract common expressions and phrases"""
        expressions = []
        
        common_patterns = [
            "Ok ok", "Thank you", "No problem", "I will try", "Ayina",
            "Actually", "Seriously", "Just", "Yeah", "Hlo", "Thnx",
            "U tell", "Wht", "Tht", "Aftr", "Evn", "Undrstud"
        ]
        
        for msg in messages:
            for pattern in common_patterns:
                if pattern.lower() in msg.lower():
                    expressions.append(pattern)
        
        return list(set(expressions))
    
    def generate_response(self, user_input: str, context: str = "") -> str:
        """Generate response in Yaswanth's style"""
        
        if not self.personality_prompt:
            self.personality_prompt = self.build_personality_prompt()
        
        # Build conversation context
        conversation_history = "\n".join([
            f"User: {ctx['user']}\nYaswanth: {ctx['response']}" 
            for ctx in self.conversation_context[-3:]  # Last 3 exchanges
        ])
        
        system_prompt = self.personality_prompt
        
        user_prompt = f"""Previous conversation:
{conversation_history}

Current context: {context}

User (Indu): {user_input}

Respond as Yaswanth would - naturally mixing Telugu-English, being caring but not desperate, and showing genuine interest. Keep it conversational and authentic."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Store in conversation context
            self.conversation_context.append({
                'user': user_input,
                'response': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            return ai_response
            
        except Exception as e:
            return f"Sorry, technical issue ayindhi. {str(e)}"
    
    def chat_interface(self):
        """Simple chat interface for testing"""
        print("🤖 Yaswanth AI Twin Ready!")
        print("Type 'quit' to exit\n")
        
        while True:
            user_input = input("Indu: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Yaswanth: Bye! Take care 😊")
                break
            
            if user_input:
                response = self.generate_response(user_input)
                print(f"Yaswanth: {response}\n")

if __name__ == "__main__":
    # Initialize AI Twin
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("API key required!")
        exit(1)
    
    ai_twin = YaswanthAITwin(api_key)
    
    # Load chat data
    ai_twin.load_chat_data()
    
    # Start chat interface
    ai_twin.chat_interface()
