# Snapchat Memories Downloader - Setup Guide

Download and organize all your Snapchat memories with this step-by-step guide. No coding experience needed — you don't need to type a single command.

Go to [windows_guide.md](https://github.com/jennathor/download_snap_memories/blob/main/Windows/windows_guide.md) for the Windows guide, or [mac_guide.md](https://github.com/jennathor/download_snap_memories/blob/main/macOS/mac_guide.md) for the Mac guide. Each guide walks through two downloads (your Snapchat export, and this project) and one double-click (`Start.bat` on Windows, `Start.command` on Mac). That one click installs everything, finds your export automatically, downloads your memories, and verifies them — no other steps required.

---
---
---


## Quick Start Checklist

- [ ] Download your Snapchat `memories_history.html` export (below)
- [ ] Download this project as a ZIP (below)
- [ ] Double-click `Start.bat` / `Start.command` (does everything else automatically)

---

## Before You Start

### 1. Download your Snapchat `memories_history.html` file (from Snapchat's data export)
1. Log in to Snapchat's Account Portal
   - Open your browser and go to **https://accounts.snapchat.com/v2/download-my-data**
   - Log in with your Snapchat credentials.

2. Select Data Types
   - Scroll down and make sure the checkbox for **"Memories and Other Media"** is selected.

3. Request Data
   - Follow the remaining steps on the page (such as selecting a date range and confirming your email) until you can click the **Submit Request / Export** button.
   - Snapchat will notify you that your request is being processed.

4. Wait for the Email
   - Snapchat will email you a link to download your data.
   - This can take anywhere from a few minutes to several hours or even days, depending on the size of your data.

5. Download the Data Zip
   - When you receive the email, click the link to download the ZIP file containing your data.

6. Extract the ZIP File
   - Extract the ZIP file.
   - Inside, you will find a folder named something like `mydata ~ [date]`.

7. Locate the HTML File
   - Open the `html` folder inside the extracted data.
   - Locate the file named `memories_history.html` and download it. Keep it in your Downloads folder for now.

### 2. Download This Project

Go to https://github.com/jennathor/download_snap_memories, click the green **Code** button → **Download ZIP**, then unzip it. See the [Windows guide](https://github.com/jennathor/download_snap_memories/blob/main/Windows/windows_guide.md) or [Mac guide](https://github.com/jennathor/download_snap_memories/blob/main/macOS/mac_guide.md) for exactly where to click next.

### 3. Where Your Memories Will Be Stored

The Start script saves everything to a `Memories` folder in your home folder automatically (`C:\Users\<you>\Memories` on Windows, `/Users/<you>/Memories` on Mac) — no need to choose or create anything yourself. Just make sure that drive has plenty of free space; your memories could be many gigabytes!

---

## Troubleshooting

The `Start.bat` / `Start.command` file handles installation and setup automatically, so most of these only come up if you used the Manual Setup section in your platform guide instead.

### "Command not found" errors
- Make sure you completed all installation steps
- Restart your computer
- For Mac: Make sure you're using `python3` not `python`

### "Permission denied" errors
- **Windows:** Right-click Command Prompt and choose "Run as administrator"
- **Mac:** Make sure your chosen Memories folder is one you have write access to (the default, your home folder, always works)

### Downloads are failing
- Check your internet connection
- Make sure `memories_history.html` is in the correct folder
- Run `memories_verify_recover.py` to retry failed downloads
- Made sure you Snapchat data has not expired (as of 12/17/25: data requests expire 3 days after receiving them)

### FFmpeg errors
- Double-check that FFmpeg is installed (`ffmpeg -version` in Terminal/Command Prompt)
- If you used Manual Setup, make sure the `FFMPEG_PATH` in both scripts matches your installation

### Still stuck?
- Make sure all three files (`memories_download.py`, `memories_verify_recover.py`, `memories_history.html`) are in your Memories folder
- If you used Manual Setup, check that both scripts have the exact same `BASE_DIR` and `FFMPEG_PATH` values

---

## What These Scripts Do

- **memories_download.py** - Downloads all your Snapchat memories from the HTML file, organizes them by year, and merges any overlays (text, stickers, etc.)
- **memories_verify_recover.py** - Checks that all files downloaded correctly, retries any failures, and can remove duplicate files

Both scripts create detailed logs in the `_logs` folder so you can track what happened.







