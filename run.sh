#!/bin/bash

# Personal Codex Agent - Run Script
echo "🤖 Starting Personal Codex Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your OpenAI API key before running again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create src directory if it doesn't exist
mkdir -p src

# Run the application
echo "🚀 Launching Streamlit app..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0