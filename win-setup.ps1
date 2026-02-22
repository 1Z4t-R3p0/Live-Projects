# ====================================
#       Windows Setup Script
# ====================================

$DOTFILES_REPO = "https://github.com/1Z4t-R3p0/Live-Projects.git"
$DOTFILES_DIR = "$HOME\dotfiles"
$CONFIG_BASE = "$HOME\.config"

# 1. Install Dependencies (requires Winget)
Write-Host "Installing dependencies..." -ForegroundColor Cyan

$apps = @("Git.Git", "Alacritty.Alacritty", "Starship.Starship", "Neovim.Neovim")

foreach ($app in $apps) {
    Write-Host "Installing $app..." -ForegroundColor Gray
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
function Set-Config {
    param($src, $dest)
    if (Test-Path $dest) {
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        Write-Host "Backing up existing config: $dest" -ForegroundColor Gray
        Move-Item $dest "$dest.bak.$timestamp" -Force
    }
    $parent = Split-Path $dest
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent }
    Copy-Item -Path $src -Destination $dest -Recurse -Force
}

# Apply configurations (matches dwm-installer pattern)
if (Test-Path "$DOTFILES_DIR\alacritty") {
    Set-Config "$DOTFILES_DIR\alacritty" "$env:APPDATA\alacritty"
}

Write-Host ""
Write-Host "============================" -ForegroundColor Green
Write-Host " Windows Setup Complete!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
Write-Host "Please restart your terminal."
