# Snapchat Memories Downloader - Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed!

Look at [windows_guide.md](https://github.com/jennathor/download_snap_memories/blob/main/Windows/windows_guide.md) for a Windows specific user guide, and [mac_guide.md](https://github.com/jennathor/download_snap_memories/blob/main/macOS/mac_guide.md) for a Mac specific guide.

---
---
---


## Quick Start Checklist

Estimated total time: **30-45 minutes** (plus download time)

- [ ] Install Python, FFmpeg, and Python packages (2 min)
- [ ] Set up folders (5 min)
- [ ] Edit paths in scripts - windows only (5 min)
- [ ] Run the download script (varies - could be hours)
- [ ] Run the verification script (optional, if some items didn't download)

---

## Before You Start

### 1. Find Your Username

**Windows:**
- Press `Windows Key + R`
- Type `cmd` and press Enter
- Type `echo %USERNAME%` and press Enter
- Write down the username shown (you'll need this exact spelling)

**Mac:**
- Press `Command (⌘) + Space`
- Type `terminal` and press Enter
- Type `whoami` and press Enter
- Write down the username shown

### 2. Choose Where to Store Your Memories

**Recommended location:**
- **Windows:** `C:\Memories`
- **Mac:** Your home folder `/Users/YourUsername/Memories`

**Tip:** Pick somewhere with plenty of storage space. Your memories could be many gigabytes!

### 3. Download Required Files

Before starting, download these files:
1. `memories_download.py` (the main download script)
2. `memories_verify_recover.py` (checks your downloads)
3. Your Snapchat `memories_history.html` file (from Snapchat's data export)

Keep them in your Downloads folder for now.

---

## Troubleshooting

### "Command not found" errors
- Make sure you completed all installation steps
- Restart your computer
- For Mac: Make sure you're using `python3` not `python`

### "Permission denied" errors
- **Windows:** Right-click Command Prompt and choose "Run as administrator"
- **Mac:** You may need to run `chmod +x memories_download.py` first

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




