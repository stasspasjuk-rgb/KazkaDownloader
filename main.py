import customtkinter as ctk
import threading
import subprocess
import os
import sys
import json
import urllib.request
import zipfile
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    from win10toast import ToastNotifier
    TOAST = ToastNotifier()
except Exception:
    TOAST = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#1A0F08"
CARD = "#2A1A0F"
CARD_BORDER = "#3D2818"
ACCENT = "#E85D04"
ACCENT_HOVER = "#F48C06"
TEXT = "#F5E6D3"
MUTED = "#C4A882"
BTN_DARK = "#3D2818"
BTN_DARK_HOVER = "#4A3220"
ENTRY_BG = "#23150C"

YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"
TG_URL = "https://t.me/kazkavpn"

TEXTS = {
    "ru": {
        "subtitle": "YouTube • TikTok • Instagram и другие",
        "url_label": "Ссылка на видео",
        "url_placeholder": "https://www.youtube.com/watch?v=...",
        "paste": "Вставить",
        "path_label": "Папка сохранения",
        "browse": "Обзор...",
        "quality_label": "Качество",
        "quality_best": "Максимальное",
        "quality_audio": "Только аудио (MP3)",
        "download": "СКАЧАТЬ",
        "downloading": "ЗАГРУЗКА...",
        "log_label": "Лог",
        "history": "История",
        "tg": "Telegram",
        "ad_title": "Знал ли ты?",
        "ad_text": "Что kazkavpn один из лучших дешёвых VPN с обходом\nблокировок, а также бесплатный пробный период.\n\nСнизу ты видишь промокод который даёт тебе\nскидку 10% на покупку VPN!",
        "ad_channel": "@kazkavpn",
        "ad_btn": "KAZKADOWNLOADER",
        "err_url": "Введите ссылку на видео",
        "err_path": "Укажите корректную папку",
        "start_dl": "Начинаю",
        "quality": "Качество",
        "folder": "Папка",
        "done": "✓ Загрузка завершена",
        "fail": "✗ Ошибка загрузки",
        "exit_title": "Выход",
        "exit_msg": "Загрузка идёт. Выйти?",
        "warn_title": "Ошибка",
        "dl_ytdlp": "Скачиваю yt-dlp.exe...",
        "ytdlp_ok": "yt-dlp.exe готов",
        "ytdlp_found": "yt-dlp.exe найден",
        "dl_ffmpeg": "Скачиваю ffmpeg (это может занять время)...",
        "extract_ffmpeg": "Распаковываю ffmpeg.exe...",
        "ffmpeg_ok": "ffmpeg.exe готов",
        "ffmpeg_found": "ffmpeg.exe найден",
        "ready": "Готов к загрузке",
        "prep_error": "Ошибка подготовки",
        "notif_start": "Загрузка начата",
        "notif_done": "Загрузка завершена",
        "hist_title": "История загрузок",
        "hist_empty": "История пуста",
        "hist_clear": "Очистить",
        "hist_close": "Закрыть",
        "lang_title": "Выбери язык",
        "lang_ru": "Русский",
        "lang_en": "English"
    },
    "en": {
        "subtitle": "YouTube • TikTok • Instagram and more",
        "url_label": "Video URL",
        "url_placeholder": "https://www.youtube.com/watch?v=...",
        "paste": "Paste",
        "path_label": "Save folder",
        "browse": "Browse...",
        "quality_label": "Quality",
        "quality_best": "Best",
        "quality_audio": "Only Audio (MP3)",
        "download": "DOWNLOAD",
        "downloading": "DOWNLOADING...",
        "log_label": "Log",
        "history": "History",
        "tg": "Telegram",
        "ad_title": "Did you know?",
        "ad_text": "Kazkavpn is one of the best low-cost VPNs for bypassing blocks,\nand it also offers a free trial period.\n\nBelow, you'll find a promo code that gives you a\n10% discount on your VPN purchase!",
        "ad_channel": "@kazkavpn",
        "ad_btn": "KAZKADOWNLOADER",
        "err_url": "Enter a video URL",
        "err_path": "Specify a valid folder",
        "start_dl": "Starting",
        "quality": "Quality",
        "folder": "Folder",
        "done": "✓ Download completed",
        "fail": "✗ Download failed",
        "exit_title": "Exit",
        "exit_msg": "Download in progress. Exit?",
        "warn_title": "Error",
        "dl_ytdlp": "Downloading yt-dlp.exe...",
        "ytdlp_ok": "yt-dlp.exe ready",
        "ytdlp_found": "yt-dlp.exe found",
        "dl_ffmpeg": "Downloading ffmpeg (this may take a while)...",
        "extract_ffmpeg": "Extracting ffmpeg.exe...",
        "ffmpeg_ok": "ffmpeg.exe ready",
        "ffmpeg_found": "ffmpeg.exe found",
        "ready": "Ready to download",
        "prep_error": "Preparation error",
        "notif_start": "Download started",
        "notif_done": "Download completed",
        "hist_title": "Download History",
        "hist_empty": "History is empty",
        "hist_clear": "Clear",
        "hist_close": "Close",
        "lang_title": "Select language",
        "lang_ru": "Русский",
        "lang_en": "English"
    }
}


def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.resolve()


def get_config_path():
    return get_app_dir() / "config.json"


def get_history_path():
    return get_app_dir() / "history.json"


def load_config():
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(data):
    try:
        with open(get_config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_history():
    path = get_history_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(data):
    try:
        with open(get_history_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def notify(title, message):
    if TOAST:
        try:
            TOAST.show_toast(title, message, duration=4, threaded=True)
        except Exception:
            pass


class LanguageDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select
        self.title("")
        self.geometry("420x280")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 280) // 2
        self.geometry(f"420x280+{x}+{y}")

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18, border_width=1, border_color=CARD_BORDER)
        card.pack(expand=True, fill="both", padx=28, pady=28)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(18, 10))

        title = ctk.CTkLabel(
            top,
            text="Выбери язык",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT
        )
        title.pack(side="left")

        tg = ctk.CTkButton(
            top,
            text="✈️ @kazkavpn",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=12,
            width=110,
            height=28,
            command=lambda: webbrowser.open(TG_URL)
        )
        tg.pack(side="right")

        flags = ctk.CTkFrame(card, fg_color="transparent")
        flags.pack(pady=(8, 6))

        ru_frame = ctk.CTkFrame(flags, fg_color="transparent")
        ru_frame.pack(side="left", padx=30)

        ru_flag = ctk.CTkLabel(ru_frame, text="🇷🇺", font=ctk.CTkFont(size=42))
        ru_flag.pack()

        ru_btn = ctk.CTkButton(
            ru_frame,
            text="Русский",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=ACCENT,
            text_color=TEXT,
            corner_radius=12,
            width=100,
            height=34,
            command=lambda: self.select("ru")
        )
        ru_btn.pack(pady=(8, 0))

        en_frame = ctk.CTkFrame(flags, fg_color="transparent")
        en_frame.pack(side="left", padx=30)

        en_flag = ctk.CTkLabel(en_frame, text="🇺🇸", font=ctk.CTkFont(size=42))
        en_flag.pack()

        en_btn = ctk.CTkButton(
            en_frame,
            text="English",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=ACCENT,
            text_color=TEXT,
            corner_radius=12,
            width=100,
            height=34,
            command=lambda: self.select("en")
        )
        en_btn.pack(pady=(8, 0))

    def select(self, lang):
        self.grab_release()
        self.destroy()
        self.on_select(lang)


class AdWindow(ctk.CTkToplevel):
    def __init__(self, parent, lang, on_close):
        super().__init__(parent)
        self.on_close = on_close
        t = TEXTS[lang]
        self.title("")
        self.geometry("460x340")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 460) // 2
        y = (self.winfo_screenheight() - 340) // 2
        self.geometry(f"460x340+{x}+{y}")

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=18, border_width=1, border_color=CARD_BORDER)
        card.pack(expand=True, fill="both", padx=26, pady=26)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(16, 8))

        left_title = ctk.CTkFrame(top, fg_color="transparent")
        left_title.pack(side="left")

        lock = ctk.CTkLabel(left_title, text="🔒", font=ctk.CTkFont(size=22))
        lock.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(
            left_title,
            text=t["ad_title"],
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT
        )
        title.pack(side="left")

        tg = ctk.CTkButton(
            top,
            text="✈️ @kazkavpn",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=12,
            width=110,
            height=28,
            command=lambda: webbrowser.open(TG_URL)
        )
        tg.pack(side="right")

        text = ctk.CTkLabel(
            card,
            text=t["ad_text"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MUTED,
            justify="left"
        )
        text.pack(padx=22, pady=(4, 16), anchor="w")

        btn = ctk.CTkButton(
            card,
            text=t["ad_btn"],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=ACCENT,
            text_color=TEXT,
            corner_radius=14,
            height=42,
            command=self.close
        )
        btn.pack(pady=(0, 20), padx=50, fill="x")

    def close(self):
        self.grab_release()
        self.destroy()
        self.on_close()


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, lang, history, on_clear):
        super().__init__(parent)
        self.lang = lang
        self.history = history
        self.on_clear = on_clear
        t = TEXTS[lang]
        self.title(t["hist_title"])
        self.geometry("520x400")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.transient(parent)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"520x400+{x}+{y}")

        frame = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=CARD_BORDER)
        frame.pack(expand=True, fill="both", padx=18, pady=18)

        title = ctk.CTkLabel(
            frame,
            text=t["hist_title"],
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=ACCENT
        )
        title.pack(pady=(16, 10))

        self.list_box = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=ENTRY_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10,
            text_color=TEXT,
            wrap="word",
            state="disabled"
        )
        self.list_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        if not history:
            self.list_box.configure(state="normal")
            self.list_box.insert("end", t["hist_empty"])
            self.list_box.configure(state="disabled")
        else:
            self.list_box.configure(state="normal")
            for item in reversed(history[-50:]):
                line = f"{item.get('date', '')}  |  {item.get('quality', '')}\n{item.get('url', '')}\n{item.get('path', '')}\n{'-'*40}\n"
                self.list_box.insert("end", line)
            self.list_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))

        clear_btn = ctk.CTkButton(
            btn_frame,
            text=t["hist_clear"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=10,
            height=36,
            command=self.clear
        )
        clear_btn.pack(side="left")

        close_btn = ctk.CTkButton(
            btn_frame,
            text=t["hist_close"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=10,
            height=36,
            command=self.destroy
        )
        close_btn.pack(side="right")

    def clear(self):
        self.on_clear()
        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")
        self.list_box.insert("end", TEXTS[self.lang]["hist_empty"])
        self.list_box.configure(state="disabled")


class KazkaDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_dir = get_app_dir()
        self.ytdlp_path = self.app_dir / "yt-dlp.exe"
        self.ffmpeg_path = self.app_dir / "ffmpeg.exe"
        self.config = load_config()
        self.lang = self.config.get("language")
        self.history = load_history()
        self.is_downloading = False
        self.binaries_ready = False
        self.download_path = str(Path.home() / "Downloads")

        self.title("KAZKADOWNLOADER")
        self.geometry("680x600")
        self.minsize(580, 540)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        icon_path = self.app_dir / "logo.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 680) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"680x600+{x}+{y}")

        self.withdraw()

        if self.lang not in ("ru", "en"):
            self.after(80, self.show_lang_dialog)
        else:
            self.after(80, self.init_after_lang)

    def show_lang_dialog(self):
        LanguageDialog(self, self.on_lang_selected)

    def on_lang_selected(self, lang):
        self.lang = lang
        self.config["language"] = lang
        save_config(self.config)
        self.init_after_lang()

    def init_after_lang(self):
        self.build_ui()
        self.apply_language()
        self.deiconify()
        self.after(150, self.show_ad)

    def show_ad(self):
        AdWindow(self, self.lang, self.after_ad)

    def after_ad(self):
        self.prepare_binaries()

    def t(self, key):
        return TEXTS[self.lang].get(key, key)

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(18, 6))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")

        self.title_label = ctk.CTkLabel(
            left,
            text="KAZKADOWNLOADER",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT
        )
        self.title_label.pack(side="left")

        self.subtitle_label = ctk.CTkLabel(
            left,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=MUTED
        )
        self.subtitle_label.pack(side="left", padx=(10, 0), pady=(5, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self.tg_btn = ctk.CTkButton(
            right,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0088cc",
            hover_color="#0099dd",
            text_color="#FFFFFF",
            corner_radius=8,
            width=90,
            height=32,
            command=self.open_tg
        )
        self.tg_btn.pack(side="left", padx=(0, 8))

        self.hist_btn = ctk.CTkButton(
            right,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=8,
            width=90,
            height=32,
            command=self.show_history
        )
        self.hist_btn.pack(side="left", padx=(0, 8))

        self.lang_btn = ctk.CTkButton(
            right,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=8,
            width=50,
            height=32,
            command=self.toggle_language
        )
        self.lang_btn.pack(side="left")

        main = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=CARD_BORDER)
        main.pack(fill="both", expand=True, padx=28, pady=(8, 20))

        self.url_label = ctk.CTkLabel(
            main,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MUTED,
            anchor="w"
        )
        self.url_label.pack(fill="x", padx=24, pady=(16, 6))

        url_frame = ctk.CTkFrame(main, fg_color="transparent")
        url_frame.pack(fill="x", padx=24)

        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=ENTRY_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10,
            height=40,
            text_color=TEXT
        )
        self.url_entry.pack(side="left", fill="x", expand=True)

        self.paste_btn = ctk.CTkButton(
            url_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=10,
            width=90,
            height=40,
            command=self.paste_url
        )
        self.paste_btn.pack(side="left", padx=(10, 0))

        self.path_label = ctk.CTkLabel(
            main,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MUTED,
            anchor="w"
        )
        self.path_label.pack(fill="x", padx=24, pady=(12, 6))

        path_frame = ctk.CTkFrame(main, fg_color="transparent")
        path_frame.pack(fill="x", padx=24)

        self.path_entry = ctk.CTkEntry(
            path_frame,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=ENTRY_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10,
            height=40,
            text_color=TEXT
        )
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.path_entry.insert(0, self.download_path)

        self.browse_btn = ctk.CTkButton(
            path_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_HOVER,
            text_color=TEXT,
            corner_radius=10,
            width=90,
            height=40,
            command=self.browse_folder
        )
        self.browse_btn.pack(side="left", padx=(10, 0))

        self.quality_label = ctk.CTkLabel(
            main,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MUTED,
            anchor="w"
        )
        self.quality_label.pack(fill="x", padx=24, pady=(12, 6))

        self.quality_combo = ctk.CTkComboBox(
            main,
            values=[],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=ENTRY_BG,
            border_color=CARD_BORDER,
            border_width=1,
            button_color=BTN_DARK,
            button_hover_color=BTN_DARK_HOVER,
            dropdown_fg_color=CARD,
            dropdown_hover_color=BTN_DARK,
            corner_radius=10,
            height=40,
            state="readonly",
            text_color=TEXT
        )
        self.quality_combo.pack(fill="x", padx=24)

        self.download_btn = ctk.CTkButton(
            main,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=12,
            height=48,
            state="disabled",
            command=self.start_download
        )
        self.download_btn.pack(fill="x", padx=24, pady=(18, 10))

        self.log_label = ctk.CTkLabel(
            main,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MUTED,
            anchor="w"
        )
        self.log_label.pack(fill="x", padx=24, pady=(2, 6))

        self.log_box = ctk.CTkTextbox(
            main,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=ENTRY_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10,
            text_color=TEXT,
            wrap="word",
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def apply_language(self):
        t = TEXTS[self.lang]
        self.subtitle_label.configure(text=t["subtitle"])
        self.url_label.configure(text=t["url_label"])
        self.url_entry.configure(placeholder_text=t["url_placeholder"])
        self.paste_btn.configure(text=t["paste"])
        self.path_label.configure(text=t["path_label"])
        self.browse_btn.configure(text=t["browse"])
        self.quality_label.configure(text=t["quality_label"])
        self.download_btn.configure(text=t["download"] if not self.is_downloading else t["downloading"])
        self.log_label.configure(text=t["log_label"])
        self.hist_btn.configure(text=t["history"])
        self.tg_btn.configure(text=t["tg"])
        self.lang_btn.configure(text="EN" if self.lang == "ru" else "RU")

        qualities = [
            t["quality_best"],
            "1080p",
            "720p",
            "480p",
            t["quality_audio"]
        ]
        current = self.quality_combo.get()
        self.quality_combo.configure(values=qualities)
        if current in qualities:
            self.quality_combo.set(current)
        else:
            self.quality_combo.set(qualities[0])

    def toggle_language(self):
        self.lang = "en" if self.lang == "ru" else "ru"
        self.config["language"] = self.lang
        save_config(self.config)
        self.apply_language()

    def open_tg(self):
        webbrowser.open(TG_URL)

    def show_history(self):
        HistoryWindow(self, self.lang, self.history, self.clear_history)

    def clear_history(self):
        self.history = []
        save_history(self.history)

    def paste_url(self):
        try:
            text = self.clipboard_get()
            if text:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, text.strip())
        except Exception:
            pass

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def log(self, message):
        def _update():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _update)

    def prepare_binaries(self):
        thread = threading.Thread(target=self._prepare_worker, daemon=True)
        thread.start()

    def _prepare_worker(self):
        try:
            if not self.ytdlp_path.exists():
                self.log(self.t("dl_ytdlp"))
                urllib.request.urlretrieve(YTDLP_URL, self.ytdlp_path)
                self.log(self.t("ytdlp_ok"))
            else:
                self.log(self.t("ytdlp_found"))

            if not self.ffmpeg_path.exists():
                self.log(self.t("dl_ffmpeg"))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                    tmp_path = tmp.name
                urllib.request.urlretrieve(FFMPEG_URL, tmp_path)
                self.log(self.t("extract_ffmpeg"))
                with zipfile.ZipFile(tmp_path, "r") as zf:
                    found = False
                    for name in zf.namelist():
                        norm = name.replace("\\", "/")
                        if norm.endswith("ffmpeg.exe") and "/bin/" in norm:
                            with zf.open(name) as src, open(self.ffmpeg_path, "wb") as dst:
                                dst.write(src.read())
                            found = True
                            break
                    if not found:
                        for name in zf.namelist():
                            if name.endswith("ffmpeg.exe"):
                                with zf.open(name) as src, open(self.ffmpeg_path, "wb") as dst:
                                    dst.write(src.read())
                                break
                os.unlink(tmp_path)
                self.log(self.t("ffmpeg_ok"))
            else:
                self.log(self.t("ffmpeg_found"))

            self.binaries_ready = True
            self.after(0, lambda: self.download_btn.configure(state="normal"))
            self.log(self.t("ready"))
        except Exception as e:
            self.log(f"{self.t('prep_error')}: {e}")

    def get_format_args(self, quality):
        t = TEXTS[self.lang]
        if quality == t["quality_best"]:
            return ["-f", "bestvideo+bestaudio/best"]
        if quality == "1080p":
            return ["-f", "bestvideo[height<=1080]+bestaudio/best"]
        if quality == "720p":
            return ["-f", "bestvideo[height<=720]+bestaudio/best"]
        if quality == "480p":
            return ["-f", "bestvideo[height<=480]+bestaudio/best"]
        if quality == t["quality_audio"]:
            return ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
        return ["-f", "bestvideo+bestaudio/best"]

    def start_download(self):
        if self.is_downloading or not self.binaries_ready:
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(self.t("warn_title"), self.t("err_url"))
            return

        path = self.path_entry.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showwarning(self.t("warn_title"), self.t("err_path"))
            return

        quality = self.quality_combo.get()
        self.is_downloading = True
        self.download_btn.configure(state="disabled", text=self.t("downloading"))
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        self.log(f"{self.t('start_dl')}: {url}")
        self.log(f"{self.t('quality')}: {quality}")
        self.log(f"{self.t('folder')}: {path}")
        self.log("-" * 40)

        notify("KAZKADOWNLOADER", self.t("notif_start"))

        thread = threading.Thread(
            target=self.run_download,
            args=(url, path, quality),
            daemon=True
        )
        thread.start()

    def run_download(self, url, path, quality):
        success = False
        try:
            format_args = self.get_format_args(quality)
            cmd = [
                str(self.ytdlp_path),
                "--no-playlist",
                "--newline",
                "--ffmpeg-location", str(self.ffmpeg_path),
                "-o", os.path.join(path, "%(title)s.%(ext)s"),
                *format_args,
                url
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    self.log(line)

            process.wait()
            success = process.returncode == 0

            if success:
                self.log("-" * 40)
                self.log(self.t("done"))
                notify("KAZKADOWNLOADER", self.t("notif_done"))
            else:
                self.log("-" * 40)
                self.log(self.t("fail"))
        except Exception as e:
            self.log(f"✗ {e}")
        finally:
            if success:
                entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "url": url,
                    "path": path,
                    "quality": quality
                }
                self.history.append(entry)
                if len(self.history) > 100:
                    self.history = self.history[-100:]
                save_history(self.history)
            self.after(0, self.download_finished)

    def download_finished(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text=self.t("download"))

    def on_close(self):
        if self.is_downloading:
            if messagebox.askyesno(self.t("exit_title"), self.t("exit_msg")):
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    print("Программа запустилась")
    try:
        app = KazkaDownloader()
        print("Окно создано")
        app.mainloop()
    except Exception as e:
        print("ОШИБКА:")
        print(e)
        input("Нажми Enter чтобы закрыть...")