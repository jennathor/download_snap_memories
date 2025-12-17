# Snapchat Memories Downloader - Complete Setup Guide FOR WINDOWS

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


## WINDOWS SETUP GUIDE

### Step 1: Install Python

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click the yellow "Download Python 3.12.x" button (or whatever the latest version is)
   - Save the installer file

2. **Install Python:**
   - Double-click the downloaded installer
   - **CRITICAL:** Check the box that says "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Python is installed:**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter (this opens Command Prompt)
   - Type: `python --version`
   - Press Enter
   - You should see something like "Python 3.12.0"
   - If you see an error, restart your computer and try again

---

### Step 2: Install FFmpeg

1. **Download FFmpeg:**
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Click on "ffmpeg-release-essentials.zip" (under "Release builds")
   - Save the ZIP file to your Downloads folder

2. **Extract FFmpeg:**
   - Go to your Downloads folder
   - Right-click the `ffmpeg-release-essentials.zip` file
   - Click "Extract All..."
   - Click "Extract"
   - You'll now have a folder like `ffmpeg-6.0-essentials_build`

3. **Add FFmpeg to PATH:**
   - Open the extracted folder
   - Open the `bin` folder inside it
   - Copy the folder path from the address bar (e.g., `C:\Users\YourName\Downloads\ffmpeg-6.0-essentials_build\bin`)
   
   **Now add it to your system PATH:**
   - Press `Windows Key`
   - Type "environment variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables..." button at the bottom
   - In the "System variables" section (bottom half), find and click "Path"
   - Click "Edit..."
   - Click "New"
   - Paste the FFmpeg bin folder path you copied
   - Click "OK" on all windows
   - **Restart your computer** (important!)

4. **Verify FFmpeg is installed:**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter
   - Type: `ffmpeg -version`
   - Press Enter
   - You should see version information
   - If you see an error, double-check the PATH steps above

---

### Step 3: Install Python Packages

1. **Open Command Prompt:**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

2. **Install packages:**
   - Type the command below and press Enter:
   ```bash
   pip install aiohttp aiofiles tqdm Pillow
   ```

3. **Verify installation:**
   - Type: `pip list`
   - Press Enter
   - You should see `aiohttp`, `aiofiles`, `tqdm`, and `Pillow` in the list

---

### Step 4: Set Up Your Files and Folders

1. **Download the Python scripts:**
   - Download both `memories_download.py` and `memories_verify_recover.py` files from wherever you obtained them (GitHub, email, etc.)
   - Save them to a location you'll remember (e.g., your Downloads folder, 'C:\Users\Username\Downloads')

2. **Create the main Memories folder:**
   - Open File Explorer
   - Navigate to a location where you want to store your memories
   - **Recommended:** `C:\Memories` (directly on C: drive for simplicity)
   - **Alternative:** `C:\Users\YourName\Documents\Memories`
   - Right-click in the empty space
   - Click "New" → "Folder"
   - Name it: `Memories`

3. **Move the Python scripts:**
   - Move both `memories_download.py` and `memories_verify_recover.py` into your new `Memories` folder
   - They should now be at: `C:\Memories\memories_download.py` and `C:\Memories\memories_verify_recover.py`

4. **Download your Snapchat memories HTML file:**
   - Follow Snapchat's instructions to export your memories
   - You'll receive a file called `memories_history.html` (it may be within several zipped folders - extract all layers until you find the HTML file)
   - Move `memories_history.html` into your `Memories` folder
   - It should now be at: `C:\Memories\memories_history.html`

---

### Step 5: Configure the Scripts

You need to update file paths in both scripts to match YOUR computer.

**For `memories_download.py`:**

1. Right-click the file and select "Edit with Notepad" (or "Open with" → "Notepad")
2. Find this line near the top (around line 11):
```python
BASE_DIR = Path("C:/Users/jenna/Documents/Memories")
```

3. **Change it to match where YOU created your Memories folder:**
```python
BASE_DIR = Path("C:/Memories")  # If you created it directly on C: drive
```

**OR**
```python
BASE_DIR = Path("C:/Users/YourUsername/Documents/Memories")  # If you created it in Documents
```

**Replace `YourUsername` with your actual Windows username.**

To find your username:
- Press `Windows Key + R`
- Type `cmd` and press Enter
- Type `echo %USERNAME%`
- Press Enter
- This shows your username - use this EXACT spelling

4. **Only if FFmpeg is not in your PATH** (you'll know if you got errors in Step 2), find this line (around line 17):
```python
FFMPEG_PATH = "ffmpeg"
```

Change it to the full path:
```python
FFMPEG_PATH = "C:/Users/YourUsername/Downloads/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
```

5. Save the file (Ctrl+S) and close Notepad

**For `memories_verify_recover.py`:**

1. Right-click the file and select "Edit with Notepad"
2. Find this line near the top (around line 9):
```python
BASE_DIR = Path("C:/Users/jenna/Documents/Memories")  # "C:/Users/YourUsername/Documents/Memories"
```

3. **Change it to EXACTLY match what you used in `memories_download.py`:**
```python
BASE_DIR = Path("C:/Memories")  # Must match memories_download.py
```

**OR**
```python
BASE_DIR = Path("C:/Users/YourUsername/Documents/Memories")  # Must match memories_download.py
```

4. **Only if FFmpeg is not in your PATH**, find this line (around line 15):
```python
FFMPEG_PATH = "ffmpeg"
```

Change it to the same path you used in the first script:
```python
FFMPEG_PATH = "C:/Users/YourUsername/Downloads/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
```

5. Save the file (Ctrl+S) and close Notepad

**Important:** Both scripts MUST use the same `BASE_DIR` and `FFMPEG_PATH` values!

---

### Step 6: Run the Scripts

1. **Open Command Prompt in your Memories folder:**
   - Type: `cd C:\Memories` (if Memories is directly on C: drive)
   - OR type: `cd C:\Users\YourUsername\Documents\Memories` (if in Documents)
   - Press Enter

2. **Run the download script:**
   ```bash
   python memories_download.py
   ```
   - Press Enter
   - The script will start downloading your memories
   - You'll see progress bars
   - This may take several hours depending on how many memories you have

3. **After downloading completes, run the verification script:**
   - This step may not be necessary if you had success for all of your downloads.

   ```bash
   python memories_verify_recover.py
   ```
   - Press Enter
   - This checks if everything downloaded correctly
   - It will retry any failed downloads
   - It may ask if you want to delete duplicates - type `yes` or `no`

4. **Your memories will be organized in:**
   Years folders, partial saves, and download logs
   - `C:\Memories\2024\` (if Memories is directly on C: drive)
   - OR `C:\Users\YourUsername\Documents\Memories\2024\` (if in Documents)
   - `C:\Users\YourUsername\Documents\Memories\_logs\` (download logs)
   - `C:\Users\YourUsername\Documents\Memories\partial_saves\` (any files that couldn't have overlays merged)

---