@echo off
setlocal enabledelayedexpansion
title KazkaDownloader Build and Pack

echo [1/5] Checking UPX...
if not exist "upx-win64\upx.exe" (
    echo Downloading UPX...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/upx/upx/releases/download/v4.2.4/upx-4.2.4-win64.zip' -OutFile 'upx.zip'"
    powershell -Command "Expand-Archive -Path 'upx.zip' -DestinationPath 'upx_temp' -Force"
    for /d %%D in (upx_temp\upx-*) do move "%%D" "upx-win64" >nul
    rmdir /s /q "upx_temp" >nul 2>&1
    del /f /q "upx.zip" >nul 2>&1
)

echo [2/5] Cleaning previous builds...
rmdir /s /q "build" >nul 2>&1
rmdir /s /q "dist\KazkaDownloader" >nul 2>&1
del /f /q "dist\KazkaDownloader*.7z*" >nul 2>&1

echo [3/5] Compiling with PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed --name "KazkaDownloader" --upx-dir "upx-win64" --add-data "ui;ui" --hidden-import "yt_dlp" --hidden-import "webview" --hidden-import "clr" --exclude-module "tkinter" --exclude-module "tcl" --exclude-module "tk" --exclude-module "unittest" --exclude-module "test" main.py

if not exist "dist\KazkaDownloader\KazkaDownloader.exe" (
    echo [ERROR] Build failed! Check Python/PyInstaller output above.
    pause
    exit /b 1
)

echo [4/5] Searching for 7-Zip...
set "SEVENZIP="
if exist "%ProgramFiles%\7-Zip\7z.exe" set "SEVENZIP=%ProgramFiles%\7-Zip\7z.exe"
if exist "%ProgramFiles(x86)%\7-Zip\7z.exe" set "SEVENZIP=%ProgramFiles(x86)%\7-Zip\7z.exe"

if "%SEVENZIP%"=="" (
    echo [WARNING] 7-Zip not found in default paths. Packing to regular zip...
    powershell -Command "Compress-Archive -Path 'dist\KazkaDownloader' -DestinationPath 'dist\KazkaDownloader.zip' -Force"
    goto finish
)

echo [5/5] Packing into 7z volumes under 20MB...
"%SEVENZIP%" a -t7z -mx=9 -md=64m -mfb=128 -ms=on -v19500k "dist\KazkaDownloader.7z" ".\dist\KazkaDownloader\*"

:finish
echo Done! All files are located in the dist\ folder.
pause
