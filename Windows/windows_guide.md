# Snapchat Memories Downloader - WINDOWS Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed!

---

## Quick Start Checklist

Estimated total time: **15–25 minutes** (plus Snapchat download time)

- [ ] Install Python & FFmpeg (Fast Install or Manual)
- [ ] Install Python packages
- [ ] Set up folders
- [ ] Edit output path in scripts
- [ ] Run the download script (may take hours)
- [ ] Run the verification script (optional)

---

## Before You Start

### 1. Choose Where to Store Your Memories (Step 4)

**Recommended location (this guide assumes this will be your storage location):**
- `C:\Memories`

### 3. Download Required Files

Download the following files and keep them in your **Downloads** folder for now:

1. `memories_download.py`
2. `memories_verify_recover.py`
3. Your Snapchat export file: `memories_history.html`

---
---

## WINDOWS SETUP GUIDE

## Option A (Recommended): FAST INSTALL using `winget`

### Step 1A: Install Python and FFmpeg Automatically

1. Open **Command Prompt**
   - Press `Windows Key + R`
   - Type `cmd` → press Enter
   - Ensure winget exists, type `winget --version` and press Enter

2. Run these commands **one at a time**:
   ```
   winget install Python.Python.3.12
   winget install Gyan.FFmpeg
   ```

3. **Restart your computer** (important!)

### Step 1B: Verify Installations

Open Command Prompt again and run:
```
python --version
ffmpeg -version
```
You should see version information for both.

If both work, **skip to Step 3: Install Python Packages**  
If `winget` is not available, use **Option B** below.


---

## Option B (Fallback): MANUAL INSTALL

Use this only if the Fast Install did not work.

### Step 1: Install Python (Manual)

1. Go to: https://www.python.org/downloads/
2. Click **Download Python**
3. Double-click the installer
4. **IMPORTANT:** Check **“Add Python to PATH”**
5. Click **Install Now**
6. Finish and close

Verify it exists:
```
python --version
```

### Step 2: Install FFmpeg (Manual)

1. Go to: https://www.gyan.dev/ffmpeg/builds/
2. Download **ffmpeg-release-essentials.zip**
3. Extract the ZIP file
4. Open the extracted folder → open `bin`
5. Copy the full path (example):
   ```
   C:\Users\YourUsername\Downloads\ffmpeg-6.0-essentials_build\bin
   ```

### Add FFmpeg to PATH

1. Press `Windows Key`
2. Search **environment variables**
3. Click **Edit the system environment variables**
4. Click **Environment Variables**
5. Under **System variables**, select `Path` → **Edit**
6. Click **New** → paste the FFmpeg `bin` path
7. Click **OK** on all windows
8. **Restart your computer**

Verify it exists:
```
ffmpeg -version
```
---

### Step 3: Install Python Packages

1. **Open Command Prompt:**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

2. **Install the packages:**
   - Copy and paste this command:
   ```
   pip install aiohttp aiofiles tqdm Pillow
   ```
   - Press Enter, and wait for it to finish (30 sec - 2 min)

3. **Verify it worked:**
   - Type `pip list` and press Enter
   - You should see `aiohttp`, `aiofiles`, `tqdm`, and `Pillow` in the list

---

### Step 4: Set Up Folders and Files

1. **Create your Memories folder:**
   - Open File Explorer
   - Go to `C:\`
   - Right-click in empty space → "New" → "Folder"
   - Name it: `Memories`
   - Final location: `C:\Memories`

2. **Move your files:**
   - Go to your Downloads folder
   - Move these 3 files into `C:\Memories`:
     - `memories_download.py`
     - `memories_verify_recover.py`
     - `memories_history.html`

---

### Step 5: Edit the Scripts

You'll edit **1 line in 2 files** to show where to save your memories

#### Edit Script #1: memories_download.py

1. **Open the file:**
   - Go to `C:\Memories`
   - Right-click `memories_download.py`
   - Click "Edit with Notepad"

2. **Find and change this line:**

| Line to Find (about line 10)| Change It To |
|-------------|--------------|
| `BASE_DIR = Path.home() / "Memories"` | `BASE_DIR = Path("C:/Memories")` |

3. **Save and close:**
   - Press `Ctrl + S`
   - Close Notepad

#### Edit Script #2: memories_verify_recover.py

1. **Open the file:**
   - Right-click `memories_verify_recover.py`
   - Click "Edit with Notepad"

2. **Make the EXACT SAME change:**

| Line to Find (about line 9)| Change It To |
|-------------|--------------|
| `BASE_DIR = Path.home() / "Memories"` | `BASE_DIR = Path("C:/Memories")` |

3. **Save and close:**
   - Press `Ctrl + S`
   - Close Notepad

**Important:** Both scripts must use identical paths!

---

### Step 6: Download Your Memories!

1. **Open Command Prompt in your Memories folder:**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter
   - Type `cd C:\Memories` and press Enter

2. **Start the download:**
   ```
   python memories_download.py
   ```
   - Press Enter
   - You'll see progress bars showing downloads
   - This could take several hours depending on how many memories you have
   - **Tip:** You can leave your computer on (make sure it doesn't fall asleep) and come back later

3. **Optional (if some memories failed to download): Verify & Retry Failed Downloads**
   ```
   python memories_verify_recover.py
   ```
   - Press Enter
   - This checks all files and retries any failures
   - If asked about deleting duplicates, type `yes` or `no`

---

### You're Done!

**Your memories are saved in:**
- `C:\Memories\2025\` (organized by year)
- `C:\Memories\2024\`
- `C:\Memories\2023\`
- etc.

**Other folders created:**
- `C:\Memories\_logs\` - Download logs and tracking
- `C:\Memories\partial_saves\` - Files that couldn't have overlays merged

---
---

## Troubleshooting

### "Command not found" errors
- Make sure you completed all installation steps
- Restart your computer

### "Permission denied" errors
- Right-click Command Prompt and choose "Run as administrator"

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

