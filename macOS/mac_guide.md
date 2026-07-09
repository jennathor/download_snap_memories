# Snapchat Memories Downloader - macOS Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed — you will not need to type a single command.

---

## Quick Start Checklist

Estimated total time: **under 2 minutes of clicking**, then it runs by itself (setup + download can take hours in the background).

- [ ] Download this project as a ZIP (2 min)
- [ ] Double-click `Start.command` (does everything else automatically)

---

## Before You Start

### 1. Get your Snapchat export

Download your `memories_history.html` file from Snapchat's data export (see [the main README](../README.md) for those steps) and leave it in your **Downloads** folder — you don't need to move it anywhere.

### 2. Download the project (one ZIP file)

1. Go to the GitHub repo page: https://github.com/jennathor/download_snap_memories
2. Click the green **Code** button → **Download ZIP**
3. Double-click the downloaded zip file in your Downloads folder to unzip it (Finder does this automatically) — this creates a folder named something like `download_snap_memories-main`
4. Open that folder, then open the **macOS** folder inside it — `Start.command` and both `.py` scripts are in there together

**Note:** downloading the whole project as a ZIP (rather than clicking individual file links) is what keeps `Start.command` double-clickable — clicking files one at a time strips that permission.

---

## macOS SETUP GUIDE

### Step 1: Double-click `Start.command`

- Open the folder where you unzipped the files
- Double-click **`Start.command`**
- A black Terminal window opens and does everything for you:
  - Installs Homebrew, Python, and FFmpeg if you don't already have them (you may be asked for your Mac password — typing won't show, that's normal)
  - Installs the required Python packages
  - Finds your `memories_history.html` automatically (checks the same folder, Downloads, and Desktop)
  - Creates `~/Memories` and downloads everything into it
  - Runs the verification step automatically at the end

**If nothing happens when you double-click it:** right-click `Start.command` → **Open** → click **Open** again in the popup. This is normal macOS behavior for downloaded scripts and only needs doing once.

**If it can't find your html file:** it'll ask you to drag `memories_history.html` into the window — just drag the file from Finder into the black window and press Enter.

This can take several hours for a lot of memories — the window will tell you when it's done. You can leave your computer on and come back later (make sure it doesn't fall asleep).

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

## Manual Setup (only if `Start.command` doesn't work for you)

1. **Open Terminal:** `Command (⌘) + Space` → type `terminal` → Enter
2. Install Homebrew, Python, and FFmpeg, then the Python packages:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python ffmpeg
   python3 -m pip install --user aiohttp aiofiles tqdm Pillow
   ```
3. Create a `Memories` folder in your home folder (Finder → Go → Home → New Folder), and move `memories_download.py`, `memories_verify_recover.py`, and `memories_history.html` into it.
4. In Terminal: `cd ~/Memories`, then run:
   ```bash
   python3 memories_download.py
   python3 memories_verify_recover.py
   ```

---

## Troubleshooting

### "Command not found" errors
- Make sure you completed all installation steps
- Restart your computer
- Make sure you're using `python3` not `python`

### "Permission denied" errors
- Make sure your chosen Memories folder is one you have write access to (the default, your home folder, always works)

### Downloads are failing
- Check your internet connection
- Make sure `memories_history.html` is in the correct folder
- Run `memories_verify_recover.py` to retry failed downloads
- Made sure you Snapchat data has not expired (as of 12/17/25: data requests expire 3 days after receiving them)

### FFmpeg errors
- Double-check that FFmpeg is installed (`ffmpeg -version` in Terminal)
- If you used Manual Setup, make sure the `FFMPEG_PATH` in both scripts matches your installation

### Still stuck?
- Make sure all three files (`memories_download.py`, `memories_verify_recover.py`, `memories_history.html`) are in your Memories folder
- If you used Manual Setup, check that both scripts have the exact same `BASE_DIR` and `FFMPEG_PATH` values

---

## What These Scripts Do

- **memories_download.py** - Downloads all your Snapchat memories from the HTML file, organizes them by year, and merges any overlays (text, stickers, etc.)
- **memories_verify_recover.py** - Checks that all files downloaded correctly, retries any failures, and can remove duplicate files

Both scripts create detailed logs in the `_logs` folder so you can track what happened.
