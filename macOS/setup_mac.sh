#!/bin/bash

# Snapchat Memories Downloader - Mac Setup Script (Robust / Fresh Mac)
# Handles Homebrew PATH, Xcode CLT, Apple Silicon vs Intel, and errors

set -e

print_header() {
  echo "============================================"
  echo "$1"
  echo "============================================"
  echo ""
}

print_step() {
  echo "[$1] $2"
}

print_header "Snapchat Memories Downloader - Mac Setup"

# ------------------------------
# 0. Ensure Xcode Command Line Tools
# ------------------------------
print_step "0/4" "Checking for Xcode Command Line Tools..."
if ! xcode-select -p &>/dev/null; then
  echo "Xcode Command Line Tools not found. Installing..."
  xcode-select --install
  echo "A macOS installer window should appear."
  echo "Please finish installing, then re-run this script."
  exit 1
else
  echo "Xcode Command Line Tools are installed"
fi
echo ""

# ------------------------------
# 1. Install / Load Homebrew
# ------------------------------
print_step "1/4" "Checking for Homebrew..."
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Ensure brew is on PATH (Intel + Apple Silicon)
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

if ! command -v brew &>/dev/null; then
  echo "ERROR: Homebrew installed but not available in PATH"
  echo "Please restart Terminal and re-run this script."
  exit 1
fi

echo "Homebrew ready: $(brew --version | head -n1)"
echo ""

# ------------------------------
# 2. Python
# ------------------------------
print_step "2/4" "Checking for Python 3..."
if ! command -v python3 &>/dev/null; then
  echo "Python not found. Installing via Homebrew..."
  brew install python
fi

echo "Python: $(python3 --version)"
echo ""

# ------------------------------
# 3. FFmpeg
# ------------------------------
print_step "3/4" "Checking for FFmpeg..."
if ! command -v ffmpeg &>/dev/null; then
  echo "FFmpeg not found. Installing (this may take several minutes)..."
  brew install ffmpeg
fi

echo "FFmpeg: $(ffmpeg -version | head -n1)"
echo ""

# ------------------------------
# 4. Python Packages (user-safe)
# ------------------------------
print_step "4/4" "Installing Python packages..."

python3 -m pip install --upgrade pip
python3 -m pip install --user aiohttp aiofiles tqdm Pillow

echo "Python packages installed"
echo ""

# ------------------------------
# Final Verification
# ------------------------------
print_header "Verifying installation"

ERRORS=0

check_cmd() {
  if command -v "$1" &>/dev/null; then
    echo "$1: OK"
  else
    echo "$1: NOT FOUND"
    ERRORS=$((ERRORS + 1))
  fi
}

check_cmd python3
check_cmd ffmpeg

echo ""
echo "Python packages:"
for pkg in aiohttp aiofiles tqdm Pillow; do
  if python3 -m pip show "$pkg" &>/dev/null; then
    echo "  $pkg"
  else
    echo "  $pkg (MISSING)"
    ERRORS=$((ERRORS + 1))
  fi
done

echo ""
print_header "Result"

if [ "$ERRORS" -eq 0 ]; then
  echo "SUCCESS! All dependencies installed correctly"
  echo ""
  echo "Next steps:"
  echo "1. Ensure memories_history.html is in this folder"
  echo "2. Edit paths in the Python scripts if needed"
  echo "3. Run: python3 memories_download.py"
else
  echo "Some dependencies failed to install."
  echo "Please scroll up, fix any errors, then re-run the script."
fi
