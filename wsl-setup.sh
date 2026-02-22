#!/bin/bash
set -e

# ====================================
#       WSL Ubuntu Setup Script
# ====================================

DOTFILES_REPO="https://github.com/SridharanThangaraji/dotfiles.git"
DOTFILES_DIR="$HOME/dotfiles"

echo "===================================="
echo "       WSL System Setup"
echo "===================================="

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing essential tools..."
sudo apt install -y build-essential git curl unzip neovim zsh

# Clone Dotfiles
if [ ! -d "$DOTFILES_DIR" ]; then
    echo "Cloning dotfiles repository..."
    git clone "$DOTFILES_REPO" "$DOTFILES_DIR"
fi

# Setup Oh-My-Zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Installing Oh-My-Zsh..."
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Backup and Copy Configs
mkdir -p "$HOME/.config"

apply_config() {
    local src="$1"
    local dest="$2"
    if [ -d "$dest" ]; then
        echo "Backing up existing $(basename "$dest") config..."
        mv "$dest" "${dest}.bak.$(date +%s)"
    fi
    cp -r "$src" "$dest"
}

# Example: Applying nvim config
if [ -d "$DOTFILES_DIR/nvim" ]; then
    apply_config "$DOTFILES_DIR/nvim" "$HOME/.config/nvim"
fi

echo ""
echo "============================"
echo " WSL Setup Complete!"
echo "============================"
echo "Run 'zsh' to enter your new environment."
