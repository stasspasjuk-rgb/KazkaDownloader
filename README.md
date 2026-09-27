# 🚀 KAZKADOWNLOADER

Современный десктопный загрузчик видео для Windows.

Поддерживает YouTube, TikTok, Instagram и сотни других сайтов.

[Последняя сборка](https://github.com/stasspasjuk-rgb/KazkaDownloader/releases/latest)

---

## ✨ Возможности

- 🌍 Выбор языка (Русский / English)
- ⚡ Автоматическая загрузка `yt-dlp` + `ffmpeg` при первом запуске
- 📹 Выбор качества (Максимальное, 1080p, 720p, 480p, только аудио MP3)
- 📜 История загрузок
- 🔔 Уведомления Windows
- ✈️ Кнопка быстрого перехода в Telegram-канал @kazkavpn
- 📦 Полностью портативный — всего один файл `.exe`

---

## 📥 Как скачать и запустить

1. Перейди во вкладку **Releases**
2. Скачай файл `KAZKADOWNLOADER.exe`
3. Запусти его

Больше ничего устанавливать не нужно.  
При первом запуске программа сама скачает необходимые компоненты.

---

## 🛠️ Сборка из исходников

### Требования
- Python **3.10** или новее (рекомендуется 3.11 / 3.12)

### Команды

```bash
# 1. Установка зависимостей
python -m pip install --upgrade pip
python -m pip install customtkinter pyinstaller win10toast

# 2. Сборка exe
python -m PyInstaller --noconfirm --onefile --windowed --name "KAZKADOWNLOADER" --icon=logo.ico --collect-all customtkinter main.py
```

Готовый файл появится здесь:

dist/KAZKADOWNLOADER.exe

# 📌 Примечания

Перед сборкой положи файл logo.ico в ту же папку, где лежит main.py
Программа создаёт config.json и history.json рядом с exe 


Modern desktop video downloader for Windows.

Supports YouTube, TikTok, Instagram and hundreds of other sites.

[Last Releases](https://github.com/stasspasjuk-rgb/KazkaDownloader/releases/latest)

---

## ✨ Features

- 🌍 Language selection (Russian / English)
- ⚡ Automatic download of `yt-dlp` + `ffmpeg` on first launch
- 📹 Quality selection (Best, 1080p, 720p, 480p, Audio only MP3)
- 📜 Download history
- 🔔 Windows notifications
- ✈️ Quick button to Telegram channel @kazkavpn
- 📦 Fully portable — just one `.exe` file

---

## 📥 How to Download & Run

1. Go to the **Releases** tab
2. Download `KAZKADOWNLOADER.exe`
3. Run it

Nothing else needs to be installed.  
On first launch the program will automatically download required components.

---

## 🛠️ Build from Source

### Requirements
- Python **3.10** or newer (3.11 / 3.12 recommended)

### Commands

```bash
# 1. Install dependencies
python -m pip install --upgrade pip
python -m pip install customtkinter pyinstaller win10toast

# 2. Build the executable
python -m PyInstaller --noconfirm --onefile --windowed --name "KAZKADOWNLOADER" --icon=logo.ico --collect-all customtkinter main.py
```

The ready file will be here:

dist/KAZKADOWNLOADER.exe

📌 Notes

Put logo.ico in the same folder as main.py before building
The program creates config.json and history.json next to the exe
