# Multi-Platform Setup Scripts

## Windows PowerShell Setup (`win-setup.ps1`)

```powershell
# ====================================
#       Windows Setup Script
# ====================================

$DOTFILES_REPO = "https://github.com/SridharanThangaraji/dotfiles.git"
$DOTFILES_DIR = "$HOME\dotfiles"
$CONFIG_BASE = "$HOME\.config"

# 1. Install Dependencies (requires Winget)
Write-Host "Installing dependencies..." -ForegroundColor Cyan

$apps = @("Git.Git", "Alacritty.Alacritty", "Starship.Starship", "Neovim.Neovim")

foreach ($app in $apps) {
    winget install --id $app --silent --accept-package-agreements --accept-source-agreements
}

# 2. Clone Dotfiles
if (-not (Test-Path $DOTFILES_DIR)) {
    Write-Host "Cloning dotfiles..." -ForegroundColor Green
    git clone $DOTFILES_REPO $DOTFILES_DIR
} else {
    Write-Host "Dotfiles already exist at $DOTFILES_DIR" -ForegroundColor Yellow
}

# 3. Setup Configs
function Copy-Config {
    param($src, $dest)
    if (Test-Path $dest) {
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        Write-Host "Backing up existing config: $dest" -ForegroundColor Gray
        Move-Item $dest "$dest.bak.$timestamp" -Force
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $dest)
    Copy-Item -Path $src -Destination $dest -Recurse -Force
}

# Example Config Linking (Adjust based on your repo structure)
if (Test-Path "$DOTFILES_DIR\alacritty") {
    Copy-Config "$DOTFILES_DIR\alacritty" "$env:APPDATA\alacritty"
}

Write-Host "============================" -ForegroundColor Green
Write-Host " Windows Setup Complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
```

## WSL Ubuntu Setup (`wsl-setup.sh`)

```bash
#!/bin/bash
set -e

# ====================================
#       WSL Ubuntu Setup Script
# ====================================

DOTFILES_REPO="https://github.com/SridharanThangaraji/dotfiles.git"
DOTFILES_DIR="$HOME/dotfiles"

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing essential tools..."
sudo apt install -y build-essential git curl unzip neovim zsh

# Clone Dotfiles
if [ ! -d "$DOTFILES_DIR" ]; then
    echo "Cloning dotfiles..."
    git clone "$DOTFILES_REPO" "$DOTFILES_DIR"
fi

# Setup Oh-My-Zsh (Optional)
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Installing Oh-My-Zsh..."
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Backup and Copy Configs
mkdir -p "$HOME/.config"

copy_config() {
    local src="$1"
    local dest="$2"
    if [ -d "$dest" ]; then
        echo "Backing up $dest..."
        mv "$dest" "${dest}.bak.$(date +%s)"
    fi
    cp -r "$src" "$dest"
}

# Apply configs from dotfiles
if [ -d "$DOTFILES_DIR/nvim" ]; then
    copy_config "$DOTFILES_DIR/nvim" "$HOME/.config/nvim"
fi

echo "============================"
echo " WSL Setup Complete!"
echo "============================"
```
