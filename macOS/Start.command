#!/bin/bash
# Snapchat Memories Downloader - double-click this file to run everything.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "Snapchat Memories Downloader"
echo "============================================"
echo ""

# ---- Xcode Command Line Tools ----
if ! xcode-select -p &>/dev/null; then
  echo "Installing Xcode Command Line Tools (an installer window will pop up)..."
  xcode-select --install
  echo "Finish that install, then double-click this file again."
  read -p "Press Enter to close this window..."
  exit 1
fi

# ---- Homebrew ----
if ! command -v brew &>/dev/null; then
  echo "Installing Homebrew (you'll be asked for your Mac password - typing won't show, that's normal)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
if [[ -x /opt/homebrew/bin/brew ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [[ -x /usr/local/bin/brew ]]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

# ---- Python & FFmpeg ----
command -v python3 &>/dev/null || { echo "Installing Python..."; brew install python; }
command -v ffmpeg &>/dev/null || { echo "Installing FFmpeg (this can take a few minutes)..."; brew install ffmpeg; }

# ---- Python packages ----
echo "Installing Python packages..."
python3 -m pip install --user --quiet aiohttp aiofiles tqdm Pillow

# ---- Find memories_download.py and memories_verify_recover.py ----
# They live next to this file if you downloaded the 3 files individually,
# or one folder up (the repo root) if you downloaded the whole project as a ZIP.
PY_SRC_DIR=""
for dir in "$SCRIPT_DIR" "$SCRIPT_DIR/.."; do
  if [[ -f "$dir/memories_download.py" && -f "$dir/memories_verify_recover.py" ]]; then
    PY_SRC_DIR="$dir"
    break
  fi
done

if [[ -z "$PY_SRC_DIR" ]]; then
  echo "Couldn't find memories_download.py and memories_verify_recover.py."
  echo "Make sure you downloaded the whole project (see the guide) and try again."
  read -p "Press Enter to close this window..."
  exit 1
fi

# ---- Find memories_history.html ----
HTML_FILE=""
for dir in "$SCRIPT_DIR" "$SCRIPT_DIR/.." "$HOME/Downloads" "$HOME/Desktop"; do
  if [[ -f "$dir/memories_history.html" ]]; then
    HTML_FILE="$dir/memories_history.html"
    break
  fi
done

if [[ -z "$HTML_FILE" ]]; then
  echo ""
  echo "Couldn't find memories_history.html in this folder, Downloads, or Desktop."
  echo "Drag your memories_history.html file into this window, then press Enter:"
  read HTML_FILE
  HTML_FILE="${HTML_FILE//[\"\']/}"
fi

# ---- Set up the Memories folder ----
MEMORIES_DIR="$HOME/Memories"
mkdir -p "$MEMORIES_DIR"
cp "$HTML_FILE" "$MEMORIES_DIR/memories_history.html"
cp "$PY_SRC_DIR/memories_download.py" "$MEMORIES_DIR/"
cp "$PY_SRC_DIR/memories_verify_recover.py" "$MEMORIES_DIR/"
cd "$MEMORIES_DIR"

# ---- Run! ----
echo ""
echo "Everything is set up. Your memories will be saved to: $MEMORIES_DIR"
echo "Starting the download now (this can take a while for a lot of memories)..."
echo ""
python3 memories_download.py

echo ""
echo "Download finished. Checking for anything that needs a retry..."
python3 memories_verify_recover.py

echo ""
echo "============================================"
echo "ALL DONE! Your memories are in: $MEMORIES_DIR"
echo "============================================"
read -p "Press Enter to close this window..."
