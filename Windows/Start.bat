@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo Snapchat Memories Downloader
echo ============================================
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo winget was not found. Please install Python and FFmpeg manually - see windows_guide.md
    pause
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo Installing Python...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
)

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo Installing FFmpeg...
    winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
)

where python >nul 2>&1
if errorlevel 1 goto :restart_needed
where ffmpeg >nul 2>&1
if errorlevel 1 goto :restart_needed
goto :continue

:restart_needed
echo.
echo Python or FFmpeg were just installed. Restart your computer, then
echo double-click this file again to finish setup.
pause
exit /b 1

:continue
echo Installing Python packages...
python -m pip install --quiet aiohttp aiofiles tqdm Pillow

rem memories_download.py / memories_verify_recover.py live next to this file if you
rem downloaded the 3 files individually, or one folder up (the repo root) if you
rem downloaded the whole project as a ZIP.
set "PY_SRC="
if exist "%~dp0memories_download.py" if exist "%~dp0memories_verify_recover.py" set "PY_SRC=%~dp0"
if not defined PY_SRC if exist "%~dp0..\memories_download.py" if exist "%~dp0..\memories_verify_recover.py" set "PY_SRC=%~dp0..\"

if not defined PY_SRC (
    echo Couldn't find memories_download.py and memories_verify_recover.py.
    echo Make sure you downloaded the whole project ^(see the guide^) and try again.
    pause
    exit /b 1
)

set "HTML_FILE="
if exist "%~dp0memories_history.html" set "HTML_FILE=%~dp0memories_history.html"
if not defined HTML_FILE if exist "%~dp0..\memories_history.html" set "HTML_FILE=%~dp0..\memories_history.html"
if not defined HTML_FILE if exist "%USERPROFILE%\Downloads\memories_history.html" set "HTML_FILE=%USERPROFILE%\Downloads\memories_history.html"
if not defined HTML_FILE if exist "%USERPROFILE%\Desktop\memories_history.html" set "HTML_FILE=%USERPROFILE%\Desktop\memories_history.html"

if not defined HTML_FILE (
    echo.
    echo Couldn't find memories_history.html in this folder, Downloads, or Desktop.
    echo Drag your memories_history.html file into this window, then press Enter:
    set /p HTML_FILE=^>
    set HTML_FILE=!HTML_FILE:"=!
)

set "MEMORIES_DIR=%USERPROFILE%\Memories"
if not exist "%MEMORIES_DIR%" mkdir "%MEMORIES_DIR%"
copy /Y "!HTML_FILE!" "%MEMORIES_DIR%\memories_history.html" >nul
copy /Y "%PY_SRC%memories_download.py" "%MEMORIES_DIR%\" >nul
copy /Y "%PY_SRC%memories_verify_recover.py" "%MEMORIES_DIR%\" >nul
cd /d "%MEMORIES_DIR%"

echo.
echo Everything is set up. Your memories will be saved to: %MEMORIES_DIR%
echo Starting the download now (this can take a while for a lot of memories)...
echo.
python memories_download.py

echo.
echo Download finished. Checking for anything that needs a retry...
python memories_verify_recover.py

echo.
echo ============================================
echo ALL DONE! Your memories are in: %MEMORIES_DIR%
echo ============================================
pause
