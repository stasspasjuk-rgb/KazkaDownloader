import os
import sys
import json
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog
import webview

from downloader import VideoDownloader
from storage import Storage

class AppAPI:
    def __init__(self, storage, downloader):
        self.storage = storage
        self.downloader = downloader
        self._window = None

    def set_window(self, window):
        self._window = window

    def get_state(self):
        return {
            "config": self.storage.config,
            "history": self.storage.history,
            "is_downloading": self.downloader.is_downloading,
            "has_ffmpeg": bool(self.downloader.ffmpeg_path)
        }

    def set_language(self, lang):
        if lang in ["ru", "en"]:
            self.storage.save_config({"language": lang})
            return {"success": True, "language": lang}
        return {"success": False, "error": "Invalid language"}

    def complete_onboarding(self, lang=None):
        updates = {"onboarding_completed": True}
        if lang in ["ru", "en"]:
            updates["language"] = lang
        self.storage.save_config(updates)
        return {"success": True}

    def select_folder(self):
        try:
            # First try webview file dialog
            if self._window and hasattr(self._window, 'create_file_dialog'):
                res = self._window.create_file_dialog(webview.FOLDER_DIALOG)
                if res and len(res) > 0:
                    folder = res[0]
                    self.storage.save_config({"save_dir": folder.replace("\\", "/")})
                    return {"success": True, "folder": folder.replace("\\", "/")}
        except Exception:
            pass

        # Fallback to tkinter filedialog
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            folder = filedialog.askdirectory(initialdir=self.storage.config.get("save_dir", ""))
            root.destroy()
            if folder:
                folder = folder.replace("\\", "/")
                self.storage.save_config({"save_dir": folder})
                return {"success": True, "folder": folder}
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "folder": self.storage.config.get("save_dir", "")}

    def get_clipboard(self):
        try:
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return {"success": True, "text": text}
        except Exception:
            return {"success": False, "text": ""}

    def copy_text(self, text):
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_download(self, url, save_dir, quality):
        if not url:
            return {"success": False, "error": "URL cannot be empty"}

        if not save_dir:
            save_dir = self.storage.config.get("save_dir")

        self.storage.save_config({"save_dir": save_dir, "quality": quality})

        def _on_complete(download_info):
            if download_info:
                updated_history = self.storage.add_history_entry(download_info)
                self._dispatch_js("window.onDownloadFinished", {
                    "success": True,
                    "info": download_info,
                    "history": updated_history
                })
            else:
                self._dispatch_js("window.onDownloadFinished", {
                    "success": False,
                    "history": self.storage.history
                })

        self.downloader.download(url, save_dir, quality, on_complete=_on_complete)
        return {"success": True}

    def cancel_download(self):
        self.downloader.cancel()
        return {"success": True}

    def open_file(self, filepath):
        return Storage.open_file(filepath)

    def open_folder(self, filepath):
        return Storage.open_folder(filepath)

    def delete_history_item(self, entry_id):
        updated = self.storage.remove_history_entry(entry_id)
        return {"success": True, "history": updated}

    def clear_all_history(self):
        updated = self.storage.clear_history()
        return {"success": True, "history": updated}

    def open_telegram(self):
        url = self.storage.config.get("telegram_url", "https://t.me/kazkavpn")
        webbrowser.open(url)
        return {"success": True}

    def install_ffmpeg(self):
        def _on_progress(pct):
            self._dispatch_js("window.onFfmpegProgress", {"percent": pct})

        def _on_finish(success):
            self._dispatch_js("window.onFfmpegFinish", {"success": success})

        self.downloader.download_ffmpeg(on_progress=_on_progress, on_finish=_on_finish)
        return {"success": True}

    def client_ready(self):
        self.downloader.ensure_components()
        return {"success": True}

    def _dispatch_js(self, func_name, payload):
        if not self._window:
            return
        try:
            json_str = json.dumps(payload, ensure_ascii=False)
            self._window.evaluate_js(f"{func_name}({json_str});")
        except Exception as e:
            print(f"Error dispatching JS {func_name}: {e}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    storage = Storage(base_dir)

    def log_handler(msg):
        if api and api._window:
            api._dispatch_js("window.onLog", {"message": str(msg)})
        else:
            print(f"[LOG] {msg}")

    def progress_handler(data):
        if api and api._window:
            api._dispatch_js("window.onProgress", data)

    downloader = VideoDownloader(log_callback=log_handler, progress_callback=progress_handler)
    api = AppAPI(storage, downloader)

    ui_path = os.path.join(base_dir, "ui", "index.html")

    window = webview.create_window(
        title="KazkaDownloader",
        url=f"file:///{os.path.normpath(ui_path).replace(os.sep, '/')}",
        js_api=api,
        width=980,
        height=720,
        min_size=(820, 600),
        background_color="#361703"
    )

    api.set_window(window)

    webview.start(debug=False)

if __name__ == "__main__":
    main()
