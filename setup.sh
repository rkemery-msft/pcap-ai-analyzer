#!/bin/bash

# Quick Start Script for PCAP AI Analyzer
# This script helps you get started quickly

echo "================================================"
echo "PCAP AI Analyzer - Quick Start"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    if ! python3 -m venv venv 2>/dev/null; then
        echo ""
        echo "⚠️  Virtual environment creation failed."
        echo "   On Debian/Ubuntu, you may need to install python3-venv:"
        echo "   sudo apt install python3-venv"
        echo ""
        echo "   Alternatively, you can install dependencies globally:"
        echo "   pip3 install -r requirements.txt"
        echo ""
        exit 1
    fi
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your Azure OpenAI credentials!"
    echo "   nano .env"
    echo ""
else
    echo ""
    echo "✓ .env file found"
fi

# Create sample directories
mkdir -p examples
mkdir -p output

echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure Azure OpenAI credentials:"
echo "   nano .env"
echo ""
echo "2. Sanitize a PCAP file:"
echo "   python sanitize_pcap.py --input your_capture.cap"
echo ""
echo "3. Prepare for AI analysis:"
echo "   python prepare_for_ai_analysis.py --input sanitized_capture_*.cap"
echo ""
echo "4. Run AI analysis:"
echo "   python analyze_with_ai.py --focus errors"
echo ""
echo "For more information, see README.md"
echo ""
