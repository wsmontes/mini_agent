#!/bin/bash

# Quick Setup Script for Mini Agent
# Run this to quickly set up your environment

set -e

echo "=================================="
echo "Mini Agent - Quick Setup"
echo "=================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo ""
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Copy environment template
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env with your LM Studio configuration"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Show next steps
echo ""
echo "=================================="
echo "Setup Complete! ✨"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure LM Studio is running with Qwen3-4B model"
echo "   - Download: lmstudio.ai"
echo "   - Load the Qwen3-4B-toolcalling model"
echo "   - Start the local server (port 1234)"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Edit .env if needed:"
echo "   nano .env"
echo ""
echo "4. Run the interactive agent:"
echo "   python main.py"
echo ""
echo "5. Or try the examples:"
echo "   python examples/weather_demo.py"
echo "   python examples/calculator_demo.py"
echo "   python examples/multi_tool_demo.py"
echo ""
echo "Documentation:"
echo "   docs/LM_STUDIO_SETUP.md - Setup guide"
echo "   docs/CUSTOM_TOOLS.md - Create custom tools"
echo "   docs/API_REFERENCE.md - API documentation"
echo ""
echo "=================================="
