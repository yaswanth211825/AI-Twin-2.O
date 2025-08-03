#!/usr/bin/env python3
"""
AI Twin with Database - Yaswanth's Digital Personality with Vector Memory
Advanced version with ChromaDB for semantic search and persistent memory
"""

import openai
import json
import re
import yaml
import sqlite3
import chromadb
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import hashlib

class YaswanthAITwinDB:
    def __init__(self, api_key: str, personality_file: str = "personality.yaml"):
        """Initialize the AI Twin with database support"""
        self.client = openai.OpenAI(api_key=api_key)
        self.personality_config = self.load_personality(personality_file)
        self.personality_prompt = ""
        
        # Initialize databases
        self.db_path = "ai_twin_memory.db"
        self.vector_db_path = "./chroma_db"
        self.init_sqlite_db()
        self.init_vector_db()
        
        # Load embedding model for semantic search
        print("🔄 Loading embedding model...")
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        print("✅ Embedding model loaded!")
        
        self.chat_data = []
        
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
    
    def init_sqlite_db(self):
        """Initialize SQLite database for structured data"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create conversations table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    date TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    context TEXT,
                    mood TEXT,
                    language_detected TEXT,
                    embedding_id TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create chat_history table for WhatsApp data
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_yaswanth BOOLEAN NOT NULL,
                    embedding_id TEXT UNIQUE,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("✅ SQLite database initialized!")
            
        except Exception as e:
            print(f"❌ Error initializing SQLite: {e}")
    
    def init_vector_db(self):
        """Initialize ChromaDB for vector embeddings"""
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
            
            # Create collections
            self.conversations_collection = self.chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"description": "AI Twin conversations with Indu"}
            )
            
            self.chat_history_collection = self.chroma_client.get_or_create_collection(
                name="chat_history", 
                metadata={"description": "WhatsApp chat history"}
            )
            
            print("✅ ChromaDB vector database initialized!")
            
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {e}")
    
    def generate_embedding_id(self, text: str) -> str:
        """Generate unique ID for embedding"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def detect_language_mix(self, text: str) -> str:
        """Detect language mix in text"""
        telugu_chars = len(re.findall(r'[అ-౯]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if telugu_chars > english_chars:
            return "Telugu-dominant"
        elif english_chars > telugu_chars:
            return "English-dominant"
        else:
            return "Mixed"
    
    def detect_mood(self, text: str) -> str:
        """Simple mood detection"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['happy', 'good', 'great', 'awesome', 'nice', '😊', '😄', '😍']):
            return "happy"
        elif any(word in text_lower for word in ['sad', 'upset', 'angry', 'frustrated', 'bad', '😢', '😠']):
            return "negative"
        elif text.strip() in ['..', '.', '...', 'waiting', 'where']:
            return "waiting/reminder"
        else:
            return "neutral"
    
    def store_conversation(self, user_input: str, ai_response: str, context: str = ""):
        """Store conversation in both SQLite and ChromaDB"""
        try:
            timestamp = datetime.now().isoformat()
            date = datetime.now().strftime('%Y-%m-%d')
            mood = self.detect_mood(user_input)
            language = self.detect_language_mix(user_input + " " + ai_response)
            
            # Create combined text for embedding
            combined_text = f"User: {user_input} | AI: {ai_response}"
            embedding_id = self.generate_embedding_id(combined_text)
            
            # Store in SQLite
            self.cursor.execute('''
                INSERT OR REPLACE INTO conversations 
                (timestamp, date, user_input, ai_response, context, mood, language_detected, embedding_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, date, user_input, ai_response, context, mood, language, embedding_id))
            
            # Generate embedding and store in ChromaDB
            embedding = self.embedding_model.encode([combined_text])[0].tolist()
            
            self.conversations_collection.upsert(
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[{
                    "timestamp": timestamp,
                    "date": date,
                    "mood": mood,
                    "language": language,
                    "context": context
                }],
                ids=[embedding_id]
            )
            
            self.conn.commit()
            print("💾 Conversation stored in database")
            
        except Exception as e:
            print(f"❌ Error storing conversation: {e}")
    
    def load_chat_data(self, chat_folder: str = "chat_data"):
        """Load and process WhatsApp chat files into database"""
        chat_files = Path(chat_folder).glob("*.txt")
        
        for file_path in chat_files:
            print(f"📁 Processing {file_path.name}...")
            
            # Check if file already processed
            self.cursor.execute(
                "SELECT COUNT(*) FROM chat_history WHERE file_name = ?", 
                (file_path.name,)
            )
            
            if self.cursor.fetchone()[0] > 0:
                print(f"⏭️ {file_path.name} already processed, skipping...")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                messages = self._parse_whatsapp_chat(content)
                
                # Store each message
                for msg in messages:
                    self.store_chat_message(file_path.name, msg)
                
                self.chat_data.append({
                    'file': file_path.name,
                    'content': content,
                    'messages': messages
                })
        
        print(f"✅ Processed {len(self.chat_data)} chat files")
    
    def store_chat_message(self, file_name: str, message: Dict):
        """Store individual chat message in database"""
        try:
            embedding_id = self.generate_embedding_id(message['message'])
            
            # Store in SQLite
            self.cursor.execute('''
                INSERT OR REPLACE INTO chat_history 
                (file_name, timestamp, sender, message, is_yaswanth, embedding_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_name, 
                message['timestamp'], 
                message['sender'], 
                message['message'], 
                message['is_yaswanth'],
                embedding_id
            ))
            
            # Generate embedding and store in ChromaDB
            embedding = self.embedding_model.encode([message['message']])[0].tolist()
            
            self.chat_history_collection.upsert(
                embeddings=[embedding],
                documents=[message['message']],
                metadatas=[{
                    "file_name": file_name,
                    "timestamp": message['timestamp'],
                    "sender": message['sender'],
                    "is_yaswanth": message['is_yaswanth']
                }],
                ids=[embedding_id]
            )
            
        except Exception as e:
            print(f"❌ Error storing chat message: {e}")
    
    def _parse_whatsapp_chat(self, content: str) -> List[Dict]:
        """Parse WhatsApp chat format into structured messages"""
        messages = []
        lines = content.split('\n')
        current_message = None
        
        for line in lines:
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
                current_message['message'] += ' ' + line.strip()
        
        if current_message:
            messages.append(current_message)
            
        return messages
    
    def semantic_search_conversations(self, query: str, limit: int = 5, days_back: int = 7) -> List[Dict]:
        """Search for relevant conversations using semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search in conversations
            results = self.conversations_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                # Note: ChromaDB date filtering can be tricky, so we'll filter after retrieval
            )
            
            relevant_conversations = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    if datetime.strptime(metadata['date'], '%Y-%m-%d') >= (datetime.now() - timedelta(days=days_back)):
                        relevant_conversations.append({
                            'document': doc,
                            'metadata': metadata,
                            'distance': results['distances'][0][i] if 'distances' in results else 0
                        })
                    relevant_conversations.append({
                        'document': doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if 'distances' in results else 0
                    })
            
            return relevant_conversations
            
        except Exception as e:
            print(f"❌ Error in semantic search: {e}")
            return []
    
    def get_context_from_memory(self, user_input: str) -> str:
        """Get relevant context from memory using semantic search"""
        # Search for relevant conversations
        relevant_convs = self.semantic_search_conversations(user_input, limit=3)
        
        if not relevant_convs:
            return ""
        
        context = "RELEVANT PAST CONVERSATIONS:\n"
        for conv in relevant_convs:
            date = conv['metadata'].get('date', 'Unknown')
            mood = conv['metadata'].get('mood', 'neutral')
            context += f"[{date}] ({mood}) {conv['document']}\n"
        
        return context
    
    def build_personality_prompt(self) -> str:
        """Build personality prompt from YAML config"""
        if not self.personality_config:
            return "You are a helpful AI assistant."
        
        config = self.personality_config
        name = config.get('name', 'Yaswanth')
        target = config.get('target_person', 'Indu')
        context = config.get('relationship_context', 'rebuilding rapport')
        
        # Build comprehensive prompt from config
        style_points = '\n'.join([f"- {point}" for point in config.get('style', [])])
        personality_points = '\n'.join([f"- {point}" for point in config.get('personality_traits', [])])
        behavioral_points = '\n'.join([f"- {point}" for point in config.get('behavioral_traits', [])])
        
        catchphrases = ', '.join(config.get('catchphrases', []))
        voice_inspiration = ', '.join(config.get('voice_inspiration', []))
        
        personality_prompt = f"""You are {name}'s AI Twin with perfect memory. Context: {context}. You're communicating with {target}.

VOICE INSPIRATION: {voice_inspiration}

STYLE GUIDELINES:
{style_points}

PERSONALITY TRAITS:
{personality_points}

BEHAVIORAL TRAITS:
{behavioral_points}

CATCHPHRASES: {catchphrases}

CRITICAL RULES:
1. ALWAYS limit responses to 1-2 lines as specified
2. Use Telugu 80% of the time as specified
3. Be authentic to the personality described
4. Mirror {target}'s mood like a social empath
5. Use SRK's quick wit and Eminem's style
6. Never sound desperate - maintain self-respect
7. Reference past conversations when relevant

Remember: You have perfect memory of all past conversations. Use this wisely to maintain continuity and show you care."""

        return personality_prompt
    
    def generate_response(self, user_input: str, context: str = "") -> str:
        """Generate response with database-powered memory"""
        if not self.personality_prompt:
            self.personality_prompt = self.build_personality_prompt()
        
        # Get relevant context from database
        memory_context = self.get_context_from_memory(user_input)
        
        system_prompt = self.personality_prompt
        
        user_prompt = f"""{memory_context}

Current context: {context}

User (Indu): {user_input}

Respond as Yaswanth would - naturally mixing Telugu-English, being caring but not desperate. If there are relevant past conversations, acknowledge them appropriately. Keep it 1-2 lines and authentic."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Store conversation in database
            self.store_conversation(user_input, ai_response, context)
            
            return ai_response
            
        except Exception as e:
            return f"Sorry, technical issue ayindhi. {str(e)}"
    
    def chat_interface(self):
        """Enhanced chat interface with database"""
        print("🤖 Yaswanth AI Twin with Database Ready!")
        print("🧠 Perfect memory enabled with semantic search")
        print("Type 'quit' to exit\n")
        
        while True:
            user_input = input("Indu: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Yaswanth: Sarsarle, catch you later! 😊")
                break
            
            if user_input:
                response = self.generate_response(user_input)
                print(f"Yaswanth: {response}\n")
    
    def __del__(self):
        """Close database connections"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    # Get API key from environment variable or user input
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        api_key = input("Enter your OpenAI API key: ").strip()
        
    if not api_key:
        print("❌ API key required!")
        exit(1)
    
    print("🚀 Initializing AI Twin with Database...")
    ai_twin = YaswanthAITwinDB(api_key)
    
    # Load chat data into database
    print("📁 Loading chat history into database...")
    ai_twin.load_chat_data()
    
    # Start chat interface
    ai_twin.chat_interface()
