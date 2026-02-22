#!/bin/bash
set -e

echo "Setting up Cowrie Honeypot..."

# Check prerequisites
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed."
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Clone repository if needed
if [ ! -d "cowrie" ]; then
    echo "Cloning Cowrie repository..."
    git clone https://github.com/cowrie/cowrie
else
    echo "Cowrie directory already exists. Skipping clone."
fi

cd cowrie

# Set up virtual environment
if [ ! -d "cowrie-env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv cowrie-env
fi

# Activate virtual environment
source cowrie-env/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Configure settings
if [ ! -f "etc/cowrie.cfg" ]; then
    echo "Creating default configuration (etc/cowrie.cfg)..."
    cp etc/cowrie.cfg.dist etc/cowrie.cfg
    echo "Created etc/cowrie.cfg from dist template."
else
    echo "Configuration already exists."
fi

echo "Setup complete!"
echo "To start Cowrie run: cd cowrie && source cowrie-env/bin/activate && bin/cowrie start"
