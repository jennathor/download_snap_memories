# Snapchat Memories Downloader - MAC OS Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed!

---

## Quick Start Checklist

Estimated total time: **30-45 minutes** (plus download time)

- [ ] Install Python (10 min)
- [ ] Install FFmpeg (10 min)  
- [ ] Install Python packages (2 min)
- [ ] Set up folders (5 min)
- [ ] Edit paths in scripts (5 min)
- [ ] Run the download script (varies - could be hours)
- [ ] Run the verification script (optional)

---

## Before You Start

### 1. Find Your Username

- Press `Command (⌘) + Space`
- Type `terminal` and press Enter
- Type `whoami` and press Enter
- Write down the username shown

### 2. Choose Where to Store Your Memories

**Recommended location:**
- Your home folder `/Users/YourUsername/Memories`

**Tip:** Pick somewhere with plenty of storage space. Your memories could be many gigabytes!

### 3. Download Required Files

Before starting, download these files:
1. `memories_download.py` (the main download script)
2. `memories_verify_recover.py` (checks your downloads)
3. Your Snapchat `memories_history.html` file (from Snapchat's data export)

Keep them in your Downloads folder for now.

---
---

## macOS SETUP GUIDE

### Step 1: Install Python

1. **Check if you already have Python:**
   - Press `Command (⌘) + Space`
   - Type `terminal` and press Enter
   - Type `python3 --version` and press Enter
   - If you see "Python 3.8" or higher, skip to Step 2!
   - If not, continue below

2. **Install Homebrew (makes installing things easy):**
   - In Terminal, paste this entire line:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   - Press Enter
   - Enter your Mac password (you won't see it typed - that's normal)
   - Wait for it to finish

3. **Install Python:**
   - Type `brew install python` and press Enter
   - Wait for it to finish

4. **Test it worked:**
   - Type `python3 --version` and press Enter
   - You should see: `Python 3.12.x` (or similar)
   - If you see an error: Restart your Mac and try again

---

### Step 2: Install FFmpeg

1. **Install FFmpeg:**
   - In Terminal, type:
   ```
   brew install ffmpeg
   ```
   - Press Enter, and wait (this takes 5-10 min)

2. **Test it worked:**
   - Type `ffmpeg -version` and press Enter
   - You should see version information
   - If you see an error: Run `brew install ffmpeg` again

---

### Step 3: Install Python Packages

1. **Open Terminal** (if not already open):
   - Press `Command (⌘) + Space`
   - Type `terminal` and press Enter

2. **Install the packages:**
   - Copy and paste this command:
   ```
   pip3 install aiohttp aiofiles tqdm Pillow
   ```
   - Press Enter, and wait for it to finish (30 sec - 2 min)

3. **Test it worked:**
   - Type `pip3 list` and press Enter
   - You should see `aiohttp`, `aiofiles`, `tqdm`, and `Pillow` in the list

---

### Step 4: Set Up Folders and Files

1. **Create your Memories folder:**
   - Open Finder
   - Click "Go" in the menu bar → "Home"
   - Right-click in empty space → "New Folder"
   - Name it: `Memories`
   - Final location: `/Users/YourUsername/Memories`

2. **Move your files:**
   - Go to your Downloads folder
   - Move these 3 files into your new `Memories` folder:
     - `memories_download.py`
     - `memories_verify_recover.py`
     - `memories_history.html`

**Tip:** All three files should now be in your Memories folder

---

### Step 5: Edit the Scripts

You need to tell the scripts where to find your files. You'll edit **2 lines in 2 files**.

#### Edit Script #1: memories_download.py

1. **Open the file:**
   - Go to your Memories folder
   - Right-click `memories_download.py`
   - Click "Open With" → "TextEdit"
   - If it opens with formatting: Click "Format" menu → "Make Plain Text"

2. **Find and change these lines:**

| Line to Find (about line 10)| Change It To |
|-------------|--------------|
| `BASE_DIR = Path("C:/Users/jenna/Documents/Memories")` | `BASE_DIR = Path.home() / "Memories"` |
| `FFMPEG_PATH = "ffmpeg"` | Leave as-is |

**Only change FFMPEG_PATH if** you got errors in Step 2:
- **For M1/M2/M3 Macs:** `FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"`
- **For Intel Macs:** `FFMPEG_PATH = "/usr/local/bin/ffmpeg"`

3. **Save and close:**
   - Press `Command + S`
   - Close TextEdit

#### Edit Script #2: memories_verify_recover.py

1. **Open the file:**
   - Right-click `memories_verify_recover.py`
   - Click "Open With" → "TextEdit"
   - If it opens with formatting: Click "Format" menu → "Make Plain Text"

2. **Make the EXACT SAME changes:**

| Line to Find | Change It To |
|-------------|--------------|
| `BASE_DIR = Path("C:/Users/jenna/Documents/Memories")` | `BASE_DIR = Path.home() / "Memories"` |
| `FFMPEG_PATH = "ffmpeg"` | Leave as-is (or use same FFmpeg path as Script #1) |

3. **Save and close:**
   - Press `Command + S`
   - Close TextEdit

**Important:** Both scripts must use identical paths!

---

### Step 6: Download Your Memories!

1. **Open Terminal in your Memories folder:**
   - Press `Command (⌘) + Space`
   - Type `terminal` and press Enter
   - Type `cd ~/Memories` and press Enter

2. **Start the download:**
   ```
   python3 memories_download.py
   ```
   - Press Enter
   - You'll see progress bars showing downloads
   - This could take several hours depending on how many memories you have
   - **Tip:** You can leave your computer on (make sure it doesn't fall asleep) and come back later

3. **After downloads finish, verify everything worked:**
 (Optional step, if all items were successfully downloaded, you're done!)
   ```
   python3 memories_verify_recover.py
   ```
   - Press Enter
   - This checks all files and retries any failures
   - If asked about deleting duplicates, type `yes` or `no`

---

### You're Done!

**Your memories are saved in:**
- `~/Memories/2025/` (organized by year)
- `~/Memories/2024/`
- `~/Memories/2023/`
- etc.

**Other folders created:**
- `~/Memories/_logs/` - Download logs and tracking
- `~/Memories/partial_saves/` - Files that couldn't have overlays merged

---
---

## Troubleshooting

### "Command not found" errors
- Make sure you completed all installation steps
- Restart your computer
- Make sure you're using `python3` not `python`

### "Permission denied" errors
- You may need to run `chmod +x memories_download.py` first

### Downloads are failing
- Check your internet connection
- Make sure `memories_history.html` is in the correct folder
- Run `memories_verify_recover.py` to retry failed downloads
- Made sure you Snapchat data has not expired (as of 12/17/25: data requests expire 3 days after receiving them)

### FFmpeg errors
- Double-check that FFmpeg is installed (`ffmpeg -version` in Terminal/Command Prompt)
- Make sure the FFMPEG_PATH in both scripts matches your installation

### Still stuck?
- Check that both scripts have the exact same BASE_DIR and FFMPEG_PATH values
- Make sure all three files (`memories_download.py`, `memories_verify_recover.py`, `memories_history.html`) are in your Memories folder
- Verify you replaced "YourUsername" with your actual username

---

## What These Scripts Do

- **memories_download.py** - Downloads all your Snapchat memories from the HTML file, organizes them by year, and merges any overlays (text, stickers, etc.)
- **memories_verify_recover.py** - Checks that all files downloaded correctly, retries any failures, and can remove duplicate files

Both scripts create detailed logs in the `_logs` folder so you can track what happened.
