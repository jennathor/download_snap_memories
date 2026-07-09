# Snapchat Memories Downloader - WINDOWS Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed — you will not need to type a single command.

---

## Quick Start Checklist

Estimated total time: **under 2 minutes of clicking**, then it runs by itself (setup + download can take hours in the background).

- [ ] Download this project as a ZIP (2 min)
- [ ] Double-click `Start.bat` (does everything else automatically)

---

## Before You Start

### 1. Get your Snapchat export

Download your `memories_history.html` file from Snapchat's data export (see [the main README](../README.md) for those steps) and leave it in your **Downloads** folder — you don't need to move it anywhere.

### 2. Download the project (one ZIP file)

1. Go to the GitHub repo page: https://github.com/jennathor/download_snap_memories
2. Click the green **Code** button → **Download ZIP**
3. In File Explorer, right-click the downloaded zip file in your Downloads folder → **Extract All...** → **Extract** — this creates a folder named something like `download_snap_memories-main`
4. Open that folder, then open the **Windows** folder inside it — `Start.bat` and both `.py` scripts are in there together

---
---

## WINDOWS SETUP GUIDE

### Step 1: Double-click `Start.bat`

- Open the folder where you extracted the files
- Double-click **`Start.bat`**
- A black Command Prompt window opens and does everything for you:
  - Installs Python and FFmpeg if you don't already have them (using Windows' built-in `winget` installer)
  - Installs the required Python packages
  - Finds your `memories_history.html` automatically (checks the same folder, Downloads, and Desktop)
  - Creates `C:\Users\<you>\Memories` and downloads everything into it
  - Runs the verification step automatically at the end

**If it says to restart your computer:** Python or FFmpeg were just installed and need a restart to be recognized. Restart, then double-click `Start.bat` again — it'll pick up right where it left off.

**If it can't find your html file:** it'll ask you to drag `memories_history.html` into the window — just drag the file from File Explorer into the black window and press Enter.

**If Windows shows a blue "Windows protected your PC" popup:** click **More info** → **Run anyway**. This is normal for downloaded scripts and only needs doing once.

This can take several hours for a lot of memories — the window will tell you when it's done. You can leave your computer on and come back later (make sure it doesn't fall asleep).

---

### You're Done!

**Your memories are saved in:**
- `C:\Users\<you>\Memories\2025\` (organized by year)
- `C:\Users\<you>\Memories\2024\`
- `C:\Users\<you>\Memories\2023\`
- etc.

**Other folders created:**
- `...\Memories\_logs\` - Download logs and tracking
- `...\Memories\partial_saves\` - Files that couldn't have overlays merged

---
---

## Manual Setup (only if `Start.bat` doesn't work for you)

### Option A: FAST INSTALL using `winget`

1. Open **Command Prompt** (`Windows Key + R` → type `cmd` → Enter)
2. Run these commands one at a time:
   ```
   winget install Python.Python.3.12
   winget install Gyan.FFmpeg
   ```
3. **Restart your computer**
4. Verify: `python --version` and `ffmpeg -version` should both print a version

### Option B: MANUAL INSTALL (if winget isn't available)

1. Python: go to https://www.python.org/downloads/, download and run the installer, and check **"Add Python to PATH"** before clicking Install.
2. FFmpeg: go to https://www.gyan.dev/ffmpeg/builds/, download **ffmpeg-release-essentials.zip**, extract it, then add its `bin` folder to your PATH (Windows Key → search **environment variables** → **Edit the system environment variables** → **Environment Variables** → select `Path` under System variables → **Edit** → **New** → paste the `bin` folder path). Restart your computer.

### Then, for either option:

1. Install the Python packages:
   ```
   pip install aiohttp aiofiles tqdm Pillow
   ```
2. Create a `Memories` folder (e.g. `C:\Memories`) and move `memories_download.py`, `memories_verify_recover.py`, and `memories_history.html` into it.
3. Open Command Prompt, `cd` into that folder, and run:
   ```
   python memories_download.py
   python memories_verify_recover.py
   ```

**Note:** the scripts save to your home folder's `Memories` folder by default. If you used a different folder like `C:\Memories`, open each `.py` file in Notepad and change the `BASE_DIR = Path.home() / "Memories"` line near the top to `BASE_DIR = Path("C:/Memories")` — make the exact same change in both files.

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
- Double-check that FFmpeg is installed (`ffmpeg -version` in Command Prompt)
- If you used Manual Setup, make sure the `FFMPEG_PATH` in both scripts matches your installation

### Still stuck?
- Make sure all three files (`memories_download.py`, `memories_verify_recover.py`, `memories_history.html`) are in your Memories folder
- If you used Manual Setup, check that both scripts have the exact same `BASE_DIR` and `FFMPEG_PATH` values

---

## What These Scripts Do

- **memories_download.py** - Downloads all your Snapchat memories from the HTML file, organizes them by year, and merges any overlays (text, stickers, etc.)
- **memories_verify_recover.py** - Checks that all files downloaded correctly, retries any failures, and can remove duplicate files

Both scripts create detailed logs in the `_logs` folder so you can track what happened.

