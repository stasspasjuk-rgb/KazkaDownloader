import os
import sys
import json
import uuid
import subprocess

CONFIG_FILE = "config.json"
HISTORY_FILE = "history.json"

DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
    DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

class Storage:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, CONFIG_FILE)
        self.history_path = os.path.join(self.base_dir, HISTORY_FILE)
        self.config = self._load_config()
        self.history = self._load_history()

    def _load_config(self):
        default_config = {
            "language": "ru",
            "save_dir": DEFAULT_DOWNLOAD_DIR.replace("\\", "/"),
            "onboarding_completed": False,
            "quality": "max",
            "promocode": "KAZKADOWNLOADER",
            "telegram_url": "https://t.me/kazkavpn"
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
            except Exception:
                pass
        return default_config

    def save_config(self, updates=None):
        if updates:
            self.config.update(updates)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
        return self.config

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_history_entry(self, entry):
        entry["id"] = str(uuid.uuid4())
        self.history.insert(0, entry)
        # Keep latest 100 entries
        self.history = self.history[:100]
        self.save_history()
        return self.history

    def remove_history_entry(self, entry_id):
        self.history = [h for h in self.history if h.get("id") != entry_id]
        self.save_history()
        return self.history

    def clear_history(self):
        self.history = []
        self.save_history()
        return self.history

    @staticmethod
    def open_file(filepath):
        if not filepath or not os.path.exists(filepath):
            return {"success": False, "error": "Файл не найден"}
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def open_folder(filepath):
        if not filepath:
            return {"success": False, "error": "Путь не указан"}
        
        folder = filepath if os.path.isdir(filepath) else os.path.dirname(filepath)
        if not os.path.exists(folder):
            return {"success": False, "error": "Папка не найдена"}
        try:
            if sys.platform == "win32":
                if os.path.isfile(filepath):
                    subprocess.Popen(f'explorer /select,"{os.path.normpath(filepath)}"')
                else:
                    subprocess.Popen(f'explorer "{os.path.normpath(folder)}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
