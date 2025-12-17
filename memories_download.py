# memories_download.py
"""
Smart Snapchat Memories Downloader
Downloads all images and videos from HTML export with built-in error handling,
ZIP processing, and comprehensive logging.
"""

from pathlib import Path

# ******* UPDATE TO YOUR SPECIFIC FILE LOCATION **********
# where you would like to save snap memories
BASE_DIR = Path.home() / "Memories"  # WINDOWS: "C:/Users/YourUsername/Documents/Memories", or `C:\Memories`


# Leave as is unless you have ffmpeg issues
# if ffmpeg errors occur, replace "ffmpeg" with full path to ffmpeg.exe here
# e.g., "C:/Users/YourUsername/Downloads/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
FFMPEG_PATH = "ffmpeg"




# ============================================================
# CONFIGURATION
# ============================================================

# Temp folder
TEMP_DIR = BASE_DIR / "_temp"
# Log folder
LOG_DIR = BASE_DIR / "_logs"
# Memories History HTML file
HTML_FILE = BASE_DIR / "memories_history.html"

MAX_CONCURRENT = 4
MAX_RETRIES = 3
TIMEOUT = 30
RETRY_BACKOFF = [2, 5, 10]  # seconds between retries

# Log files
MANIFEST_CSV = LOG_DIR / "manifest.csv"
DOWNLOAD_LOG_CSV = LOG_DIR / "download_log.csv"
ERRORS_LOG = LOG_DIR / "errors.log"
SUMMARY_TXT = LOG_DIR / "download_summary.txt"


# ============================================================
# IMPORTS/PACKAGES
# ============================================================
import asyncio, aiohttp, aiofiles, csv, os, re, subprocess, shutil
from datetime import datetime, timezone
from tqdm.asyncio import tqdm
from collections import defaultdict


# ============================================================
# SETUP
# ============================================================
def setup_directories():
    """Create necessary directories"""
    for d in [BASE_DIR, TEMP_DIR, LOG_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Clear old logs
    for f in [MANIFEST_CSV, DOWNLOAD_LOG_CSV, ERRORS_LOG, SUMMARY_TXT]:
        if f.exists():
            f.unlink()

# ============================================================
# HTML PARSING WITH DEDUPLICATION
# ============================================================
def parse_html_and_dedupe(html_path):
    """Parse HTML and remove duplicates at source"""
    print("Parsing HTML and deduplicating...")
    
    html = html_path.read_text(encoding="utf-8")
    
    # Updated regex to match the actual HTML structure
    ROW_REGEX = re.compile(
        r"<tr>\s*"
        r"<td>(?P<date>[^<]+)</td>\s*"
        r"<td>(?P<type>[^<]+)</td>\s*"
        r"<td>(?P<gps>[^<]*)</td>.*?"
        r"onclick=\"downloadMemories\('(?P<url>[^']+)'",
        re.DOTALL
    )
    
    items = []
    seen_timestamps = defaultdict(list)
    
    for m in ROW_REGEX.finditer(html):
        # Parse timestamp
        date_str = m.group("date").replace(" UTC", "")
        ts = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        
        # Extract media_id from URL
        url = m.group("url")
        mid_match = re.search(r"mid=([^&]+)", url)
        
        if not mid_match:
            print(f"Warning: No media ID found in URL: {url[:100]}...")
            continue
        
        media_id = mid_match.group(1)
        
        item = {
            "url": url,
            "timestamp": ts,
            "year": ts.year,
            "gps": m.group("gps"),
            "media_id": media_id,
            "media_type_hint": m.group("type")  # From HTML, but we'll verify via Content-Type
        }
        
        items.append(item)
        seen_timestamps[ts.isoformat()].append(item)
    
    # Deduplication: Compare both timestamp AND media_id
    seen_unique = {}  # key: "timestamp|media_id"
    duplicates_removed = 0
    
    for item in items:
        key = f"{item['timestamp'].isoformat()}|{item['media_id']}"
        
        if key in seen_unique:
            print(f"  Exact duplicate found: {item['timestamp'].isoformat()} | {item['media_id']}")
            duplicates_removed += 1
        else:
            seen_unique[key] = item
    
    unique_items = list(seen_unique.values())
    
    print(f"  Total extracted: {len(items)}")
    print(f"  Exact duplicates removed (same timestamp + media_id): {duplicates_removed}")
    print(f"  Unique items: {len(unique_items)}")
    
    return unique_items

# ============================================================
# MANIFEST CREATION
# ============================================================
def create_manifest(items):
    """Create manifest of expected files"""
    print("Creating manifest...")
    
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp_utc",
            "year",
            "media_type_hint",
            "gps",
            "original_url",
            "media_id",
            "expected_basename"
        ])
        
        for item in items:
            date_str = item["timestamp"].strftime("%Y-%m-%d_%H%M%S")
            expected_basename = f"{date_str}_{item['media_id']}"
            
            writer.writerow([
                item["timestamp"].isoformat(),
                item["year"],
                item["media_type_hint"],
                item["gps"],
                item["url"],
                item["media_id"],
                expected_basename
            ])
    
    print(f"  Manifest saved: {MANIFEST_CSV}")

# ============================================================
# SKIP EXISTING FILES
# ============================================================
def check_existing_files(items):
    """Check which files already exist and skip them"""
    print("Checking for existing files...")
    
    to_download = []
    skipped = 0
    
    for item in items:
        year_dir = BASE_DIR / str(item["year"])
        date_str = item["timestamp"].strftime("%Y-%m-%d_%H%M%S")
        base_name = f"{date_str}_{item['media_id']}"
        
        # Check for any file with this base name (we don't know extension yet)
        existing = list(year_dir.glob(f"{base_name}.*")) if year_dir.exists() else []
        
        if existing:
            print(f"  Skipping (exists): {existing[0].name}")
            skipped += 1
            continue
        
        to_download.append(item)
    
    print(f"  Already exist: {skipped}")
    print(f"  To download: {len(to_download)}")
    
    return to_download

# ============================================================
# LOGGING HELPERS
# ============================================================
csv_lock = asyncio.Lock()

async def log_download(item, status, error_type="", error_msg="", attempt=1, filename=""):
    """Log download attempt to CSV"""
    async with csv_lock:
        file_exists = DOWNLOAD_LOG_CSV.exists()
        async with aiofiles.open(DOWNLOAD_LOG_CSV, "a", encoding="utf-8") as f:
            if not file_exists:
                await f.write("timestamp_utc,media_id,filename,status,error_type,error_message,attempt_number,download_time\n")
            
            # Escape any commas in error messages
            error_msg_escaped = error_msg.replace(",", ";")
            await f.write(f"{item['timestamp'].isoformat()},{item['media_id']},{filename},{status},{error_type},{error_msg_escaped},{attempt},{datetime.now(timezone.utc).isoformat()}\n")

async def log_error(item, error_msg, attempt):
    """Log error to errors.log"""
    async with aiofiles.open(ERRORS_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        await f.write(f"[{timestamp}] MEDIA_ID: {item['media_id']} | URL: {item['url']} | ERROR: {error_msg} | ATTEMPT: {attempt}\n")

# ============================================================
# FFMPEG OVERLAY MERGE
# ============================================================
async def merge_overlay(main_path, overlay_path, output_path):
    """Merge main file with overlay using FFmpeg"""
    try:
        # Determine if video or image
        is_video = main_path.suffix.lower() == ".mp4"
        
        if is_video:
            cmd = [
                FFMPEG_PATH, "-i", str(main_path), "-i", str(overlay_path),
                "-filter_complex", "overlay",
                "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                "-c:a", "copy",
                str(output_path),
                "-y"  # overwrite
            ]
        else:
            cmd = [
                FFMPEG_PATH, "-i", str(main_path), "-i", str(overlay_path),
                "-filter_complex", "overlay",
                "-q:v", "2",  # high quality
                str(output_path),
                "-y"
            ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg failed: {stderr.decode()}")
        
        return True
        
    except Exception as e:
        raise Exception(f"Overlay merge failed: {str(e)}")

# ============================================================
# ZIP PROCESSING
# ============================================================
async def process_zip(zip_data, item, year_dir):
    """Extract ZIP, merge overlay, and return final file path"""
    import zipfile
    from io import BytesIO
    
    temp_folder = TEMP_DIR / f"zip_{item['media_id']}"
    temp_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        # Extract ZIP
        with zipfile.ZipFile(BytesIO(zip_data)) as z:
            z.extractall(temp_folder)
        
        # Find main file (check both .mp4 and .jpg)
        main_files = list(temp_folder.glob("*-main.mp4")) + list(temp_folder.glob("*-main.jpg"))
        overlay_files = list(temp_folder.glob("*-overlay.png"))
        
        if not main_files:
            raise Exception("ZIP missing -main.mp4 or -main.jpg")
        if not overlay_files:
            raise Exception("ZIP missing -overlay.png")
        
        main_path = main_files[0]
        overlay_path = overlay_files[0]
        
        # Determine output extension
        ext = main_path.suffix  # .mp4 or .jpg
        date_str = item["timestamp"].strftime("%Y-%m-%d_%H%M%S")
        output_path = year_dir / f"{date_str}_{item['media_id']}{ext}"
        
        # Merge overlay
        await merge_overlay(main_path, overlay_path, output_path)
        
        # Set timestamp
        ts_unix = item["timestamp"].timestamp()
        os.utime(output_path, (ts_unix, ts_unix))
        
        return output_path
        
    finally:
        # Cleanup temp folder
        if temp_folder.exists():
            shutil.rmtree(temp_folder, ignore_errors=True)

# ============================================================
# DOWNLOAD FUNCTION WITH RETRY
# ============================================================
async def download_item(session, item, semaphore, stats):
    """Download single item with retry logic"""
    async with semaphore:
        year_dir = BASE_DIR / str(item["year"])
        year_dir.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Download with timeout
                async with session.get(
                    item["url"],
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT)
                ) as resp:
                    
                    if resp.status != 200:
                        error_msg = f"HTTP {resp.status}"
                        
                        # Retry transient errors
                        if resp.status in [500, 502, 504] and attempt < MAX_RETRIES:
                            await log_error(item, error_msg, attempt)
                            await asyncio.sleep(RETRY_BACKOFF[attempt - 1])
                            continue
                        else:
                            raise Exception(error_msg)
                    
                    content_type = resp.headers.get("Content-Type", "").lower()
                    data = await resp.read()
                    
                    # Route based on content type
                    date_str = item["timestamp"].strftime("%Y-%m-%d_%H%M%S")
                    
                    # IMAGE
                    if "image/" in content_type:
                        output_path = year_dir / f"{date_str}_{item['media_id']}.jpg"
                        async with aiofiles.open(output_path, "wb") as f:
                            await f.write(data)
                        media_type = "Image"
                    
                    # VIDEO
                    elif "video/mp4" in content_type:
                        output_path = year_dir / f"{date_str}_{item['media_id']}.mp4"
                        async with aiofiles.open(output_path, "wb") as f:
                            await f.write(data)
                        media_type = "Video"
                    
                    # ZIP (with overlay)
                    elif "application/zip" in content_type:
                        output_path = await process_zip(data, item, year_dir)
                        media_type = "ZippedVideo"
                    
                    else:
                        raise Exception(f"Unknown Content-Type: {content_type}")
                    
                    # Set file timestamp
                    ts_unix = item["timestamp"].timestamp()
                    os.utime(output_path, (ts_unix, ts_unix))
                    
                    # Log success
                    await log_download(item, "success", filename=output_path.name, attempt=attempt)
                    stats["success"] += 1
                    
                    return
            
            except asyncio.TimeoutError:
                error_msg = "Timeout"
                await log_error(item, error_msg, attempt)
                
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF[attempt - 1])
                    continue
                else:
                    await log_download(item, "error", "Timeout", error_msg, attempt)
                    stats["failed"] += 1
                    return
            
            except Exception as e:
                error_msg = str(e)
                await log_error(item, error_msg, attempt)
                
                # Retry transient-looking errors
                if ("HTTP 5" in error_msg or "Timeout" in error_msg) and attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF[attempt - 1])
                    continue
                else:
                    error_type = "HTTP" if "HTTP" in error_msg else "ZIP" if "ZIP" in error_msg else "Unknown"
                    await log_download(item, "error", error_type, error_msg, attempt)
                    stats["failed"] += 1
                    return

# ============================================================
# MAIN DOWNLOAD ORCHESTRATOR
# ============================================================
async def download_all(items):
    """Download all items with progress tracking"""
    print(f"\nDownloading {len(items)} items...")
    
    stats = {"success": 0, "failed": 0}
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with aiohttp.ClientSession() as session:
        tasks = [download_item(session, item, semaphore, stats) for item in items]
        
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading"):
            await coro
    
    return stats

# ============================================================
# SUMMARY REPORT
# ============================================================
def generate_summary(total_items, skipped, stats):
    """Generate final summary report"""
    summary = []
    summary.append("=" * 60)
    summary.append("SNAPCHAT MEMORIES DOWNLOAD SUMMARY")
    summary.append("=" * 60)
    summary.append(f"Total unique items in HTML: {total_items}")
    summary.append(f"Already existed (skipped): {skipped}")
    summary.append(f"Attempted to download: {total_items - skipped}")
    summary.append(f"Successfully downloaded: {stats['success']}")
    summary.append(f"Failed: {stats['failed']}")
    summary.append("=" * 60)
    
    if stats['failed'] > 0:
        summary.append(f"\nFailed items logged in: {ERRORS_LOG}")
        summary.append(f"Run memories_verify_recover.py to retry failures and verify completeness.")
    else:
        summary.append("\n✓ All downloads successful!")
    
    summary.append(f"\nLogs saved to: {LOG_DIR}")
    summary.append(f"Media saved to: {BASE_DIR}/<year>/")
    
    summary_text = "\n".join(summary)
    
    # Print to console
    print("\n" + summary_text)
    
    # Save to file
    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write(summary_text)

# ============================================================
# MAIN
# ============================================================
async def main():
    print("=" * 60)
    print("SNAPCHAT MEMORIES SMART DOWNLOADER")
    print("=" * 60)
    
    setup_directories()
    
    # Parse and dedupe
    items = parse_html_and_dedupe(HTML_FILE)
    
    # Create manifest
    create_manifest(items)
    
    # Check existing files
    to_download = check_existing_files(items)
    skipped = len(items) - len(to_download)
    
    # Download
    if to_download:
        stats = await download_all(to_download)
    else:
        print("\nNo files to download - all already exist!")
        stats = {"success": 0, "failed": 0}
    
    # Generate summary
    generate_summary(len(items), skipped, stats)

if __name__ == "__main__":

    asyncio.run(main())

