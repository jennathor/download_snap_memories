# Snapchat Memories Downloader - Complete Setup Guide FOR MAC

A comprehensive guide for downloading and organizing your Snapchat memories with zero coding experience required.

---

## What You'll Need

These scripts download your Snapchat memories from an HTML file. Here's what they require:

### Dependencies (Software/Tools)
1. **Python 3.8 or higher** - The programming language that runs the scripts
2. **FFmpeg** - A tool for processing videos and images with overlays (Ensures all text bars, stickers, etc. stay on your images)
3. **Python packages** (libraries that add functionality):
   - `aiohttp` - For downloading files from the internet
   - `aiofiles` - For saving files efficiently
   - `tqdm` - For showing progress bars
   - `Pillow` (PIL) - For checking image integrity
   - `asyncio`, `csv`, `pathlib`, `zipfile` - Built into Python (no installation needed)

---


## macOS SETUP GUIDE

### Step 1: Install Python

1. **Check if Python is already installed:**
   - Press `Command (⌘) + Space`
   - Type `terminal`
   - Press Enter
   - Type: `python3 --version`
   - Press Enter
   - If you see "Python 3.8" or higher, skip to Step 2
   - If not, continue below

2. **Install Python using Homebrew (easiest method):**
   
   **First, install Homebrew:**
   - In Terminal, paste this entire command:
```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
   - Press Enter
   - Enter your Mac password when prompted (you won't see it typed - that's normal)
   - Wait for installation to complete

   **Then install Python:**
```bash
   brew install python
```
   - Press Enter and wait

3. **Verify Python is installed:**
```bash
   python3 --version
```
   - You should see something like "Python 3.12.0"
   - If you see an error, restart your Mac and try again

---

### Step 2: Install FFmpeg

1. **Install FFmpeg using Homebrew:**
   - In Terminal, type:
```bash
   brew install ffmpeg
```
   - Press Enter
   - Wait for installation (may take 5-10 minutes)

2. **Verify FFmpeg is installed:**
```bash
   ffmpeg -version
```
   - Press Enter
   - You should see version information
   - If you see an error, run `brew install ffmpeg` again

---

### Step 3: Install Python Packages

1. **Open Terminal** (if not already open):
   - Press `Command (⌘) + Space`
   - Type `terminal`
   - Press Enter

2. **Install packages:**
   - Type the command below and press Enter:
```bash
   pip3 install aiohttp aiofiles tqdm Pillow
```

3. **Verify installation:**
```bash
   pip3 list
```
   - Press Enter
   - You should see `aiohttp`, `aiofiles`, `tqdm`, and `Pillow` in the list

---

### Step 4: Set Up Your Files and Folders

1. **Download the Python scripts:**
   - Download both `memories_download.py` and `memories_verify_recover.py` files from wherever you obtained them (GitHub, email, etc.)
   - Save them to a location you'll remember (e.g., your Downloads folder, `/Users/YourUsername/Downloads`)

2. **Create the main Memories folder:**
   - Open Finder
   - Navigate to a location where you want to store your memories
   - **Recommended:** Create `Memories` in your home folder (for simplicity)
   - **Alternative:** `Documents/Memories`
   - Right-click in the empty space
   - Click "New Folder"
   - Name it: `Memories`

3. **Move the Python scripts:**
   - Move both `memories_download.py` and `memories_verify_recover.py` into your new `Memories` folder
   - They should now be at: `/Users/YourUsername/Memories/memories_download.py` and `/Users/YourUsername/Memories/memories_verify_recover.py`

4. **Download your Snapchat memories HTML file:**
   - Follow Snapchat's instructions to export your memories
   - You'll receive a file called `memories_history.html` (it may be within several zipped folders - extract all layers until you find the HTML file)
   - Move `memories_history.html` into your `Memories` folder
   - It should now be at: `/Users/YourUsername/Memories/memories_history.html`

---

### Step 5: Configure the Scripts

You need to update file paths in both scripts to match YOUR Mac.

**For `memories_download.py`:**

1. Right-click the file and select "Open With" → "TextEdit"
   - If TextEdit opens with formatting, click "Format" menu → "Make Plain Text"
2. Find this line near the top (around line 11):
```python
BASE_DIR = Path("C:/Users/jenna/Documents/Memories")
```

3. **Change it to match where YOU created your Memories folder:**
```python
BASE_DIR = Path.home() / "Memories"  # If you created it directly in your home folder
```

**OR**
```python
BASE_DIR = Path.home() / "Documents" / "Memories"  # If you created it in Documents
```

**Note:** `Path.home()` automatically uses your Mac username, so you don't need to manually type it.

4. **Only if FFmpeg is not working** (you'll know if you got errors in Step 2), find this line (around line 17):
```python
FFMPEG_PATH = "ffmpeg"
```

Change it to the full path for your Mac type:
```python
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"  # For M1/M2/M3 Macs (Apple Silicon)
```
**OR**
```python
FFMPEG_PATH = "/usr/local/bin/ffmpeg"  # For Intel Macs
```

5. Save the file (Command+S) and close TextEdit

**For `memories_verify_recover.py`:**

1. Right-click the file and select "Open With" → "TextEdit"
   - If TextEdit opens with formatting, click "Format" menu → "Make Plain Text"
2. Find this line near the top (around line 9):
```python
BASE_DIR = Path("C:/Users/jenna/Documents/Memories")
```

3. **Change it to EXACTLY match what you used in `memories_download.py`:**
```python
BASE_DIR = Path.home() / "Memories"  # Must match memories_download.py
```

**OR**
```python
BASE_DIR = Path.home() / "Documents" / "Memories"  # Must match memories_download.py
```

4. **Only if FFmpeg is not working**, find this line (around line 15):
```python
FFMPEG_PATH = "ffmpeg"
```

Change it to the same path you used in the first script:
```python
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"  # For M1/M2/M3 Macs
```
**OR**
```python
FFMPEG_PATH = "/usr/local/bin/ffmpeg"  # For Intel Macs
```

5. Save the file (Command+S) and close TextEdit

**Important:** Both scripts MUST use the same `BASE_DIR` and `FFMPEG_PATH` values!

---

### Step 6: Run the Scripts

1. **Open Terminal in your Memories folder:**
   - Press `Command (⌘) + Space`
   - Type `terminal`
   - Press Enter
   - Type: `cd ~/Memories` (if Memories is directly in your home folder)
   - OR type: `cd ~/Documents/Memories` (if in Documents)
   - Press Enter

2. **Run the download script:**
```bash
   python3 memories_download.py
```
   - Press Enter
   - The script will start downloading your memories
   - You'll see progress bars
   - This may take several hours depending on how many memories you have

3. **After downloading completes, run the verification script:**
   - This step may not be necessary if you had success for all of your downloads.
```bash
   python3 memories_verify_recover.py
```
   - Press Enter
   - This checks if everything downloaded correctly
   - It will retry any failed downloads
   - It may ask if you want to delete duplicates - type `yes` or `no`

4. **Your memories will be organized in:**
   Years folders, partial saves, and download logs
   - `~/Memories/2024/` (if Memories is directly in your home folder)
   - OR `~/Documents/Memories/2024/` (if in Documents)
   - `~/Memories/_logs/` (download logs)
   - `~/Memories/partial_saves/` (any files that couldn't have overlays merged)

---