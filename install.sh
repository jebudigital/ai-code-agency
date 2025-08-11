#!/bin/bash

echo "🚀 Installing AI Coding Agency..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version is too old. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📥 Installing AI Coding Agency in development mode..."
pip install -e .

# Install additional dependencies
echo "📚 Installing additional dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Install models: ollama pull phind-codellama:34b-v2"
echo "3. Activate virtual environment: source venv/bin/activate"
echo "4. Run demo: python demo.py"
echo "5. Run interactive mode: python main.py --interactive"
echo ""
echo "📚 For more information, see README.md"
