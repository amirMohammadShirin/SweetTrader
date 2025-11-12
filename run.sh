#!/bin/bash

# SweetTrader Bot Startup Script

echo "🚀 Starting SweetTrader Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure it."
    echo "   cp .env.example .env"
    exit 1
fi

# Run the bot
echo "🤖 Starting bot..."
python bot.py

