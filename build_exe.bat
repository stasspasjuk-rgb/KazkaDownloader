@echo off
title Сборка KazkaDownloader EXE
echo Сборка приложения KazkaDownloader в единый исполняемый файл...

pyinstaller --noconfirm --onedir --windowed --name "KazkaDownloader" ^
    --add-data "ui;ui" ^
    --hidden-import "yt_dlp" ^
    --hidden-import "webview" ^
    --hidden-import "tkinter" ^
    --hidden-import "clr" ^
    main.py

echo.
echo Сборка завершена! Файлы находятся в папке dist\KazkaDownloader\
pause
