@echo off
title KazkaDownloader
echo Запуск KazkaDownloader...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ошибка при запуске. Убедитесь, что установлены зависимости:
    echo pip install -r requirements.txt
    pause
)
