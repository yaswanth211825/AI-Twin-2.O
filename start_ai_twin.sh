#!/bin/bash

echo "🚀 Starting AI Twin 2.0 for Interview Demo"
echo "========================================"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo "💡 The AI Twin will run in demo mode with contextual responses."
    echo "🔑 To enable full AI chat, set OPENAI_API_KEY in Codespaces secrets."
    echo ""
else
    echo "✅ OpenAI API key detected - Full AI chat enabled!"
    echo ""
fi

# Install dependencies if not already installed
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🌟 Starting AI Twin 2.0 Web Interface..."
echo "📱 Interviewers can chat with the AI directly!"
echo "🌍 Supports Telugu, English, Hindi, Malayalam, Tamil"
echo "🧠 Features: Personality replication, Semantic memory, Mood detection"
echo ""
echo "🔗 The public URL will be available in the PORTS tab"
echo "📋 Share this URL with interviewers for live demo!"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"

# Start the Flask application
python3 app.py
