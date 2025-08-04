#!/usr/bin/env python3
"""
AI Twin Web Interface
Flask web application for interactive AI Twin chat with database viewing
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sqlite3
from datetime import datetime
import json
import random
from ai_twin_db import YaswanthAITwinDB

app = Flask(__name__)
app.secret_key = 'ai_twin_secret_key_2024'

# Global AI Twin instance
ai_twin = None

def init_ai_twin():
    """Initialize AI Twin with API key"""
    global ai_twin
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OpenAI API key not found in environment variables")
        print("💡 Set it with: export OPENAI_API_KEY='your-key-here'")
        print("🌐 Website will load in demo mode")
        return False
    
    try:
        ai_twin = YaswanthAITwinDB(api_key)
        print("✅ AI Twin initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing AI Twin: {e}")
        print("🌐 Website will load in demo mode")
        return False

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global ai_twin
    
    if not ai_twin:
        # Demo responses when API key is not available
        demo_responses = [
            "Hey! I'm in demo mode right now. The full AI Twin needs an OpenAI API key to work properly. But I can still show you how cool this interface is! 🚀",
            "Namaste! I'm your AI Twin demo. In full mode, I can chat in Telugu, English, Hindi and more languages with 90%+ accuracy! 🌟",
            "Hi there! This is a preview of AI Twin 2.0. With proper setup, I can remember our conversations and chat naturally in multiple languages! ✨",
            "Hello! I'm running in demo mode. The real AI Twin analyzes WhatsApp chats and replicates your personality with semantic memory! 🧠",
            "Hey! Demo mode lo unna. Full AI Twin ki OpenAI API key kavali, but interface chala bagundi kada? 😊"
        ]
        
        import random
        demo_response = random.choice(demo_responses)
        
        return jsonify({
            'response': demo_response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'demo_mode': True
        })
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Generate AI response
        ai_response = ai_twin.generate_response(user_message)
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'user_message': user_message
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'error': str(e),
            'response': 'Sorry, technical issue ayindhi. Please try again.'
        }), 500

@app.route('/api/conversations')
def get_conversations():
    """Get recent conversations from database"""
    try:
        conn = sqlite3.connect('ai_twin_memory.db')
        cursor = conn.cursor()
        
        # Get last 20 conversations
        cursor.execute('''
            SELECT user_input, ai_response, timestamp, mood, language_detected
            FROM conversations 
            ORDER BY created_at DESC 
            LIMIT 20
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user_input': row[0],
                'ai_response': row[1],
                'timestamp': row[2],
                'mood': row[3] or 'neutral',
                'language': row[4] or 'mixed'
            })
        
        conn.close()
        return jsonify(conversations)
        
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify([])

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect('ai_twin_memory.db')
        cursor = conn.cursor()
        
        # Get conversation count
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Get chat history count
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        total_chat_messages = cursor.fetchone()[0]
        
        # Get recent activity (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM conversations 
            WHERE datetime(created_at) > datetime('now', '-1 day')
        ''')
        recent_conversations = cursor.fetchone()[0]
        
        # Get language distribution
        cursor.execute('''
            SELECT language_detected, COUNT(*) 
            FROM conversations 
            WHERE language_detected IS NOT NULL
            GROUP BY language_detected
        ''')
        language_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'total_conversations': total_conversations,
            'total_chat_messages': total_chat_messages,
            'recent_conversations': recent_conversations,
            'language_stats': language_stats
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'total_conversations': 0,
            'total_chat_messages': 0,
            'recent_conversations': 0,
            'language_stats': {}
        })

@app.route('/database')
def database_view():
    """Database viewer page"""
    return render_template('database.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🚀 Starting AI Twin Web Interface...")
    
    # Try to initialize AI Twin
    ai_initialized = init_ai_twin()
    
    if ai_initialized:
        print("🌐 Web interface starting with full AI functionality")
    else:
        print("🌐 Web interface starting in DEMO MODE")
        print("💡 To enable full AI features, set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
    
    print("💬 Chat interface: http://localhost:5000")
    print("🗄️  Database viewer: http://localhost:5000/database")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
