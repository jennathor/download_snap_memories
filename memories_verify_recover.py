# memories_verify_recover.py
"""
Snapchat Memories Verification & Recovery Tool
Verifies downloads, retries failures, resolves duplicates, and generates final report.
"""


# ******* MUST MATCH the BASE_DIR used in memories_download.py **********
# where you would like to save snap memories
BASE_DIR = Path.home() / "Memories"  # WINDOWS: "C:/Users/YourUsername/Documents/Memories" or `C:\Memories`


# Leave as is unless you have ffmpeg issues
# if ffmpeg errors occur, replace "ffmpeg" with full path to ffmpeg.exe here
# e.g., "C:/Users/YourUsername/Downloads/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
# must match the FFMPEG_PATH used in memories_download.py
FFMPEG_PATH = "ffmpeg"



# ============================================================
# CONFIGURATION
# ============================================================
TEMP_DIR = BASE_DIR / "_temp"
LOG_DIR = BASE_DIR / "_logs"
PARTIAL_SAVES_DIR = BASE_DIR / "partial_saves"

MANIFEST_CSV = LOG_DIR / "manifest.csv"
DOWNLOAD_LOG_CSV = LOG_DIR / "download_log.csv"
ERRORS_LOG = LOG_DIR / "errors.log"

VERIFICATION_REPORT = LOG_DIR / "verification_report.txt"
UNRECOVERABLE_CSV = LOG_DIR / "unrecoverable_items.csv"
DUPLICATES_CSV = LOG_DIR / "duplicates_found.csv"

MAX_CONCURRENT = 4
MAX_TOTAL_RETRIES = 5
TIMEOUT = 60
RETRY_BACKOFF = [5, 10, 20]

MIN_FILE_SIZE = 1024  # bytes


# ============================================================
# IMPORTS/PACKAGES
# ============================================================
import asyncio, aiohttp, aiofiles, csv, os, subprocess, shutil
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from tqdm.asyncio import tqdm


# ============================================================
# LOAD MANIFEST
# ============================================================
def load_manifest():
    """Load expected items from manifest"""
    print("Loading manifest...")
    
    if not MANIFEST_CSV.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_CSV}")
        print("Please run memories_download.py first!")
        return []
    
    items = []
    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
    
    print(f"  Loaded {len(items)} expected items")
    return items

# ============================================================
# SCAN DISK FOR ACTUAL FILES
# ============================================================
def scan_disk_files():
    """Scan all year folders for actual files"""
    print("Scanning disk for files...")
    
    actual_files = []
    
    for year_dir in BASE_DIR.iterdir():
        if not year_dir.is_dir() or year_dir.name.startswith("_"):
            continue
        
        if not year_dir.name.isdigit():
            continue
        
        for file_path in year_dir.glob("*"):
            if file_path.is_file():
                actual_files.append(file_path)
    
    print(f"  Found {len(actual_files)} files on disk")
    return actual_files

# ============================================================
# VERIFICATION: COMPARE MANIFEST VS DISK
# ============================================================
def verify_completeness(manifest_items, actual_files):
    """Compare expected vs actual files"""
    print("\nVerifying completeness...")
    
    # Build expected files map
    expected = {}
    for item in manifest_items:
        year = item["year"]
        basename = item["expected_basename"]
        expected[f"{year}/{basename}"] = item
    
    # Build actual files map (without extension)
    actual = {}
    for file_path in actual_files:
        year = file_path.parent.name
        basename = file_path.stem  # filename without extension
        key = f"{year}/{basename}"
        actual[key] = file_path
    
    # Find missing files
    missing = []
    for key, item in expected.items():
        if key not in actual:
            missing.append(item)
    
    # Find unexpected files
    unexpected = []
    for key, file_path in actual.items():
        if key not in expected:
            unexpected.append(file_path)
    
    # Find duplicates (same timestamp AND same media_id)
    file_keys = {}  # key: "timestamp|media_id"
    for file_path in actual_files:
        try:
            filename = file_path.stem
            # Extract timestamp and media_id from filename: YYYY-MM-DD_HHMMSS_MEDIA-ID
            parts = filename.split("_")
            if len(parts) >= 3:
                date_part = "_".join(parts[:2])  # YYYY-MM-DD_HHMMSS
                media_id_part = "_".join(parts[2:]).replace("_NO-OVERLAY", "")  # Remove NO-OVERLAY suffix if present
                key = f"{date_part}|{media_id_part}"
                
                if key not in file_keys:
                    file_keys[key] = []
                file_keys[key].append(file_path)
        except:
            continue
    
    duplicates = {k: v for k, v in file_keys.items() if len(v) > 1}
    
    print(f"  ✓ Successfully downloaded: {len(actual) - len(unexpected)}")
    print(f"  ✗ Missing files: {len(missing)}")
    print(f"  ? Unexpected files: {len(unexpected)}")
    print(f"  ⚠ True duplicates (same timestamp + media_id): {len(duplicates)}")
    
    return {
        "missing": missing,
        "unexpected": unexpected,
        "duplicates": duplicates,
        "verified": len(actual) - len(unexpected)
    }

# =================================================================
# FILE INTEGRITY CHECKS --- currently disabled as it's quite slow
# =================================================================
def check_file_integrity(actual_files):
    """Check for corrupted or suspicious files"""
    print("\nChecking file integrity...")
    
    issues = []
    
    for file_path in actual_files:
        # Check file size
        size = file_path.stat().st_size
        if size < MIN_FILE_SIZE:
            issues.append({
                "file": file_path,
                "issue": f"Suspiciously small ({size} bytes)"
            })
            continue
        
        # Check if image can be opened
        if file_path.suffix.lower() in [".jpg", ".jpeg"]:
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    img.verify()
            except Exception as e:
                issues.append({
                    "file": file_path,
                    "issue": f"Corrupted image: {str(e)}"
                })
        
        # Check if video has valid duration
        elif file_path.suffix.lower() == ".mp4":
            try:
                result = subprocess.run(
                    [FFMPEG_PATH, "-i", str(file_path)],
                    capture_output=True,
                    text=True
                )
                if "Duration: 00:00:00" in result.stderr or "Invalid" in result.stderr:
                    issues.append({
                        "file": file_path,
                        "issue": "Invalid or zero-duration video"
                    })
            except Exception as e:
                issues.append({
                    "file": file_path,
                    "issue": f"Cannot probe video: {str(e)}"
                })
    
    if issues:
        print(f"  ⚠ Found {len(issues)} files with integrity issues")
    else:
        print(f"  ✓ All files passed integrity checks")
    
    return issues

# ============================================================
# RETRY MISSING FILES
# ============================================================
async def download_item_with_fallback(session, item, semaphore, stats):
    """
    Download with fallback: if overlay merge fails, save main file only to partial_saves
    """
    import aiohttp
    import aiofiles
    import shutil
    import zipfile
    from io import BytesIO
    
    async with semaphore:
        year_dir = BASE_DIR / str(item["year"])
        year_dir.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(1, MAX_TOTAL_RETRIES + 1):
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
                        if resp.status in [500, 502, 504] and attempt < MAX_TOTAL_RETRIES:
                            await asyncio.sleep(RETRY_BACKOFF[min(attempt - 1, len(RETRY_BACKOFF) - 1)])
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
                    
                    # VIDEO
                    elif "video/mp4" in content_type:
                        output_path = year_dir / f"{date_str}_{item['media_id']}.mp4"
                        async with aiofiles.open(output_path, "wb") as f:
                            await f.write(data)
                    
                    # ZIP (with overlay) - WITH FALLBACK
                    elif "application/zip" in content_type:
                        try:
                            # Try normal overlay merge using FFmpeg
                            temp_folder = TEMP_DIR / f"zip_{item['media_id']}"
                            temp_folder.mkdir(parents=True, exist_ok=True)
                            
                            try:
                                # Extract ZIP
                                with zipfile.ZipFile(BytesIO(data)) as z:
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
                                output_path = year_dir / f"{date_str}_{item['media_id']}{ext}"
                                
                                # Merge overlay with FFmpeg
                                is_video = main_path.suffix.lower() == ".mp4"
                                
                                if is_video:
                                    cmd = [
                                        FFMPEG_PATH, "-i", str(main_path), "-i", str(overlay_path),
                                        "-filter_complex", "overlay",
                                        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                                        "-c:a", "copy",
                                        str(output_path),
                                        "-y"
                                    ]
                                else:
                                    cmd = [
                                        FFMPEG_PATH, "-i", str(main_path), "-i", str(overlay_path),
                                        "-filter_complex", "overlay",
                                        "-q:v", "2",
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
                                
                                # Success - set timestamp
                                ts_unix = item["timestamp"].timestamp()
                                os.utime(output_path, (ts_unix, ts_unix))
                                
                            finally:
                                # Cleanup temp folder
                                if temp_folder.exists():
                                    shutil.rmtree(temp_folder, ignore_errors=True)
                        
                        except Exception as merge_error:
                            # FALLBACK: Save main file without overlay to partial_saves
                            print(f"\n  ⚠ Overlay merge failed for {item['media_id']}, saving without overlay...")
                            
                            temp_folder = TEMP_DIR / f"zip_fallback_{item['media_id']}"
                            temp_folder.mkdir(parents=True, exist_ok=True)
                            
                            try:
                                # Extract ZIP
                                with zipfile.ZipFile(BytesIO(data)) as z:
                                    z.extractall(temp_folder)
                                
                                # Find main file
                                main_files = list(temp_folder.glob("*-main.mp4")) + list(temp_folder.glob("*-main.jpg"))
                                
                                if not main_files:
                                    raise Exception("ZIP missing main file for fallback")
                                
                                main_path = main_files[0]
                                ext = main_path.suffix
                                
                                # Save to partial_saves folder instead
                                PARTIAL_SAVES_DIR.mkdir(parents=True, exist_ok=True)
                                output_path = PARTIAL_SAVES_DIR / f"{date_str}_{item['media_id']}_NO-OVERLAY{ext}"
                                
                                # Copy main file
                                shutil.copy(main_path, output_path)
                                
                                # Set timestamp
                                ts_unix = item["timestamp"].timestamp()
                                os.utime(output_path, (ts_unix, ts_unix))
                                
                                stats["partial"] += 1
                                return
                                
                            finally:
                                # Cleanup temp folder
                                if temp_folder.exists():
                                    shutil.rmtree(temp_folder, ignore_errors=True)
                    
                    else:
                        raise Exception(f"Unknown Content-Type: {content_type}")
                    
                    # Set file timestamp for non-zip files
                    ts_unix = item["timestamp"].timestamp()
                    os.utime(output_path, (ts_unix, ts_unix))
                    
                    stats["success"] += 1
                    return
            
            except asyncio.TimeoutError:
                if attempt < MAX_TOTAL_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF[min(attempt - 1, len(RETRY_BACKOFF) - 1)])
                    continue
                else:
                    stats["failed"] += 1
                    return
            
            except Exception as e:
                error_msg = str(e)
                
                # Retry transient-looking errors
                if ("HTTP 5" in error_msg or "Timeout" in error_msg) and attempt < MAX_TOTAL_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF[min(attempt - 1, len(RETRY_BACKOFF) - 1)])
                    continue
                else:
                    stats["failed"] += 1
                    return

async def retry_missing_files(missing_items):
    """Retry downloading missing files"""
    if not missing_items:
        print("\nNo missing files to retry")
        return {"success": 0, "failed": 0}
    
    print(f"\nRetrying {len(missing_items)} missing files...")
    
    # Check download log for previous attempts
    previous_attempts = defaultdict(int)
    if DOWNLOAD_LOG_CSV.exists():
        with open(DOWNLOAD_LOG_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                previous_attempts[row["media_id"]] = int(row.get("attempt_number", 0))
    
    # Filter items that haven't exceeded max retries
    to_retry = []
    unrecoverable = []
    
    for item in missing_items:
        attempts = previous_attempts.get(item["media_id"], 0)
        if attempts >= MAX_TOTAL_RETRIES:
            unrecoverable.append(item)
        else:
            to_retry.append(item)
    
    if unrecoverable:
        print(f"  ⚠ {len(unrecoverable)} items already exceeded max retries (marked unrecoverable)")
    
    if not to_retry:
        return {"success": 0, "failed": len(unrecoverable), "partial": 0}
    
    stats = {"success": 0, "failed": 0, "partial": 0}
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in to_retry:
            # Convert manifest item back to download item format
            download_item_data = {
                "url": item["original_url"],
                "timestamp": datetime.fromisoformat(item["timestamp_utc"]),
                "year": int(item["year"]),
                "gps": item["gps"],
                "media_id": item["media_id"],
                "media_type_hint": item["media_type_hint"]
            }
            tasks.append(download_item_with_fallback(session, download_item_data, semaphore, stats))
        
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Retrying"):
            await coro
    
    print(f"  ✓ Successfully recovered: {stats['success']}")
    print(f"  ⚠ Partial saves (without overlay): {stats['partial']}")
    print(f"  ✗ Still failed: {stats['failed']}")
    
    return stats

# ============================================================
# DUPLICATE RESOLUTION
# ============================================================
def resolve_duplicates(duplicates, auto_delete=False):
    """Identify and optionally remove duplicate files (same timestamp AND media_id)"""
    if not duplicates:
        print("\nNo true duplicates found")
        return
    
    print(f"\nResolving {len(duplicates)} true duplicate groups (same timestamp + media_id)...")
    
    resolved = []
    
    for key, files in duplicates.items():
        timestamp_part, media_id_part = key.split("|")
        print(f"\n  Duplicate: {timestamp_part} | {media_id_part}")
        
        # Compare file sizes
        file_info = []
        for f in files:
            size = f.stat().st_size
            print(f"    - {f.name} ({size} bytes)")
            file_info.append({"path": f, "size": size})
        
        # Keep largest file
        file_info.sort(key=lambda x: x["size"], reverse=True)
        to_keep = file_info[0]["path"]
        to_delete = [x["path"] for x in file_info[1:]]
        
        print(f"    → Keeping: {to_keep.name}")
        
        if auto_delete:
            for f in to_delete:
                print(f"    → Deleting: {f.name}")
                f.unlink()
        else:
            print(f"    → Would delete: {', '.join([f.name for f in to_delete])}")
        
        resolved.append({
            "key": key,
            "kept": to_keep,
            "deleted": to_delete,
            "auto_deleted": auto_delete
        })
    
    # Save duplicates report
    with open(DUPLICATES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "media_id", "kept_file", "deleted_files", "action_taken"])
        for item in resolved:
            timestamp_part, media_id_part = item["key"].split("|")
            writer.writerow([
                timestamp_part,
                media_id_part,
                item["kept"].name,
                ", ".join([f.name for f in item["deleted"]]),
                "deleted" if item["auto_deleted"] else "identified_only"
            ])
    
    if not auto_delete:
        print(f"\n  Duplicates logged to: {DUPLICATES_CSV}")
        print(f"  Re-run with auto_delete=True to remove them")

# ============================================================
# CLEANUP UNEXPECTED FILES
# ============================================================
def cleanup_unexpected(unexpected_files, auto_delete=False):
    """Remove files not in manifest"""
    if not unexpected_files:
        print("\nNo unexpected files found")
        return
    
    print(f"\nFound {len(unexpected_files)} unexpected files:")
    
    for f in unexpected_files:
        print(f"  - {f.relative_to(BASE_DIR)}")
    
    if auto_delete:
        for f in unexpected_files:
            print(f"  Deleting: {f.name}")
            f.unlink()
        print(f"  ✓ Deleted {len(unexpected_files)} unexpected files")
    else:
        print(f"\n  Re-run with auto_delete=True to remove them")

# ============================================================
# GENERATE UNRECOVERABLE REPORT
# ============================================================
def generate_unrecoverable_report(missing_items, errors_log_path):
    """Create CSV of items that couldn't be downloaded"""
    if not missing_items:
        print("\n✓ No unrecoverable items!")
        return
    
    print(f"\nGenerating unrecoverable items report...")
    
    # Load error log to get last error for each item
    last_errors = {}
    if errors_log_path.exists():
        with open(errors_log_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r"MEDIA_ID: ([^\s]+).*ERROR: ([^\|]+)", line)
                if match:
                    last_errors[match.group(1)] = match.group(2).strip()
    
    with open(UNRECOVERABLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp_utc",
            "year",
            "media_id",
            "gps",
            "original_url",
            "last_error"
        ])
        
        for item in missing_items:
            writer.writerow([
                item["timestamp_utc"],
                item["year"],
                item["media_id"],
                item["gps"],
                item["original_url"],
                last_errors.get(item["media_id"], "Unknown error")
            ])
    
    print(f"  ✗ {len(missing_items)} unrecoverable items logged to: {UNRECOVERABLE_CSV}")

# ============================================================
# FINAL REPORT
# ============================================================
def generate_final_report(manifest_count, verification_results, retry_stats): #, integrity_issues):
    """Generate comprehensive final report"""
    report = []
    report.append("=" * 70)
    report.append("SNAPCHAT MEMORIES VERIFICATION & RECOVERY REPORT")
    report.append("=" * 70)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("MANIFEST SUMMARY")
    report.append("-" * 70)
    report.append(f"Total items expected (from HTML): {manifest_count}")
    report.append("")
    
    report.append("VERIFICATION RESULTS")
    report.append("-" * 70)
    report.append(f"Successfully verified: {verification_results['verified']}")
    report.append(f"Missing files: {len(verification_results['missing'])}")
    report.append(f"Unexpected files: {len(verification_results['unexpected'])}")
    report.append(f"Duplicate timestamps: {len(verification_results['duplicates'])}")
    report.append("")
    
    if retry_stats:
        report.append("RECOVERY ATTEMPTS")
        report.append("-" * 70)
        report.append(f"Successfully recovered: {retry_stats['success']}")
        report.append(f"Failed to recover: {retry_stats['failed']}")
        report.append("")
    
    # if integrity_issues:
    #     report.append("INTEGRITY ISSUES")
    #     report.append("-" * 70)
    #     for issue in integrity_issues[:10]:  # Show first 10
    #         report.append(f"  - {issue['file'].name}: {issue['issue']}")
    #     if len(integrity_issues) > 10:
    #         report.append(f"  ... and {len(integrity_issues) - 10} more")
    #     report.append("")
    
    # Calculate final stats
    still_missing = len(verification_results['missing']) - retry_stats.get('success', 0)
    total_on_disk = verification_results['verified'] + retry_stats.get('success', 0)
    completeness = (total_on_disk / manifest_count * 100) if manifest_count > 0 else 0
    
    report.append("FINAL STATUS")
    report.append("-" * 70)
    report.append(f"Total files on disk: {total_on_disk}")
    report.append(f"Still missing: {still_missing}")
    report.append(f"Completeness: {completeness:.2f}%")
    report.append("")
    
    if still_missing > 0:
        report.append(f"⚠ Unrecoverable items logged to: {UNRECOVERABLE_CSV}")
    else:
        report.append("✓ ALL ITEMS SUCCESSFULLY DOWNLOADED!")
    
    report.append("")
    report.append("GENERATED FILES")
    report.append("-" * 70)
    report.append(f"Verification report: {VERIFICATION_REPORT}")
    if still_missing > 0:
        report.append(f"Unrecoverable items: {UNRECOVERABLE_CSV}")
    if verification_results['duplicates']:
        report.append(f"Duplicates found: {DUPLICATES_CSV}")
    report.append("")
    report.append("=" * 70)
    
    report_text = "\n".join(report)
    
    # Print to console
    print("\n" + report_text)
    
    # Save to file
    with open(VERIFICATION_REPORT, "w", encoding="utf-8") as f:
        f.write(report_text)

# ============================================================
# MAIN
# ============================================================
async def main():
    print("=" * 70)
    print("SNAPCHAT MEMORIES VERIFICATION & RECOVERY")
    print("=" * 70)
    
    # Load manifest
    manifest_items = load_manifest()
    if not manifest_items:
        return
    
    # Scan disk
    actual_files = scan_disk_files()
    
    # Verify completeness
    verification_results = verify_completeness(manifest_items, actual_files)
    
    # Check integrity
    #integrity_issues = check_file_integrity(actual_files)
    
    # Retry missing files
    retry_stats = await retry_missing_files(verification_results["missing"])
    
    # After retries, check what's still missing
    actual_files_after = scan_disk_files()
    verification_after = verify_completeness(manifest_items, actual_files_after)
    
    # Generate unrecoverable report
    generate_unrecoverable_report(verification_after["missing"], ERRORS_LOG)
    
    # Handle duplicates (requires user confirmation)
    print("\n" + "=" * 70)
    if verification_after["duplicates"]:
        response = input(f"Found {len(verification_after['duplicates'])} duplicate groups. Delete duplicates? (yes/no): ")
        auto_delete = response.lower() == "yes"
        resolve_duplicates(verification_after["duplicates"], auto_delete=auto_delete)
    
    # Handle unexpected files (requires user confirmation)
    if verification_after["unexpected"]:
        response = input(f"Found {len(verification_after['unexpected'])} unexpected files. Delete them? (yes/no): ")
        auto_delete = response.lower() == "yes"
        cleanup_unexpected(verification_after["unexpected"], auto_delete=auto_delete)
    
    # Generate final report
    generate_final_report(
        len(manifest_items),
        verification_after,
        retry_stats#,
        #integrity_issues
    )
    
    print(f"\n✓ Verification complete. See {VERIFICATION_REPORT} for details.")

if __name__ == "__main__":
    import re  # needed for unrecoverable report

    asyncio.run(main())
