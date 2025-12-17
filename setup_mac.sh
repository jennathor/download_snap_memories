#!/bin/bash

# Snapchat Memories Downloader - Mac Setup Script
# This script automatically installs all dependencies

echo "============================================"
echo "Snapchat Memories Downloader - Mac Setup"
echo "============================================"
echo ""

# Check if Homebrew is installed
echo "[1/4] Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    echo "You may be prompted for your password."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == 'arm64' ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    echo "Homebrew installed successfully"
else
    echo "Homebrew is already installed"
fi
echo ""

# Install Python
echo "[2/4] Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Installing Python..."
    brew install python
    echo "Python installed successfully"
else
    python3 --version
    echo "Python is already installed"
fi
echo ""

# Install FFmpeg
echo "[3/4] Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Installing FFmpeg..."
    echo "(This may take 5-10 minutes)"
    brew install ffmpeg
    echo "FFmpeg installed successfully"
else
    echo "FFmpeg is already installed"
fi
echo ""

# Install Python packages
echo "[4/4] Installing Python packages..."
pip3 install aiohttp aiofiles tqdm Pillow
echo "Python packages installed successfully"
echo ""

# Final verification
echo "============================================"
echo "Verifying installation..."
echo "============================================"
echo ""

ERRORS=0

# Check Python
if command -v python3 &> /dev/null; then
    echo "Python: $(python3 --version)"
else
    echo "Python: NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

# Check FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "FFmpeg: Installed"
else
    echo "FFmpeg: NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

# Check Python packages
echo ""
echo "Python packages:"
for package in aiohttp aiofiles tqdm Pillow; do
    if pip3 show $package &> /dev/null; then
        echo "  $package"
    else
        echo "  $package"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "============================================"

if [ $ERRORS -eq 0 ]; then
    echo "SUCCESS! All dependencies installed!"
    echo "============================================"
    echo ""
    echo "Next steps:"
    echo "1. Make sure memories_history.html is in this folder"
    echo "2. Edit the paths in both .py scripts (see README)"
    echo "3. Run: python3 memories_download.py"
    echo ""
else
    echo "Some dependencies failed to install"
    echo "============================================"
    echo ""
    echo "Please check the errors above and try again."
    echo "You may need to restart Terminal and re-run this script."
    echo ""
fi
