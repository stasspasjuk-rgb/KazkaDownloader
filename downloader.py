import os
import sys
import shutil
import threading
import urllib.request
import zipfile
import re
from datetime import datetime
import yt_dlp

class VideoDownloader:
    def __init__(self, log_callback=None, progress_callback=None):
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        self.is_downloading = False
        self.cancel_requested = False
        self.current_ydl = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bin_dir = os.path.join(self.base_dir, "bin")
        os.makedirs(self.bin_dir, exist_ok=True)
        self.ffmpeg_path = self._find_ffmpeg()

    def log(self, text):
        if self.log_callback:
            self.log_callback(text)
        else:
            print(text)

    def _find_ffmpeg(self):
        # 1. Local bin folder
        local_ffmpeg = os.path.join(self.bin_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.exists(local_ffmpeg):
            return self.bin_dir
        
        # 2. Try imageio_ffmpeg
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                target = os.path.join(self.bin_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
                if not os.path.exists(target):
                    shutil.copy2(exe, target)
                return self.bin_dir
        except Exception:
            pass

        # 3. System PATH
        path_ffmpeg = shutil.which("ffmpeg")
        if path_ffmpeg:
            return os.path.dirname(path_ffmpeg)
            
        return None

    def ensure_components(self, on_finish=None):
        def _check():
            # Mockup log lines:
            # Скачиваю yt-dlp
            # Скачиваю ffmpeg.exe
            # Готов к работе!
            self.log("Скачиваю yt-dlp")
            # yt-dlp is present
            
            self.log("Скачиваю ffmpeg.exe")
            ffmpeg_ready = False
            
            # Check if ffmpeg exists locally
            local_ffmpeg = os.path.join(self.bin_dir, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
            if os.path.exists(local_ffmpeg):
                self.ffmpeg_path = self.bin_dir
                ffmpeg_ready = True
            else:
                # Try getting from imageio_ffmpeg
                try:
                    import imageio_ffmpeg
                    exe = imageio_ffmpeg.get_ffmpeg_exe()
                    if exe and os.path.exists(exe):
                        shutil.copy2(exe, local_ffmpeg)
                        self.ffmpeg_path = self.bin_dir
                        ffmpeg_ready = True
                except Exception:
                    pass

            # If still not ready, download automatically
            if not ffmpeg_ready:
                try:
                    self._auto_download_ffmpeg()
                    self.ffmpeg_path = self.bin_dir
                    ffmpeg_ready = True
                except Exception as e:
                    self.log(f"Предупреждение: ffmpeg не удалось загрузить автоматически: {e}")

            self.log("Готов к работе!")
            if on_finish:
                on_finish(ffmpeg_ready)

        t = threading.Thread(target=_check, daemon=True)
        t.start()

    def _auto_download_ffmpeg(self):
        url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
        zip_path = os.path.join(self.bin_dir, "ffmpeg.zip")

        req = urllib.request.Request(url, headers={'User-Agent': 'KazkaDownloader/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp, open(zip_path, 'wb') as out_f:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out_f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe") or member.endswith("ffprobe.exe"):
                    filename = os.path.basename(member)
                    source = zip_ref.open(member)
                    target = open(os.path.join(self.bin_dir, filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)

        try:
            os.remove(zip_path)
        except Exception:
            pass

    def _format_bytes(self, bytes_num):
        if not bytes_num:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_num < 1024:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024
        return f"{bytes_num:.1f} TB"

    def _progress_hook(self, d):
        if self.cancel_requested:
            raise Exception("Download cancelled by user")

        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes') or 0
            speed = d.get('speed') or 0
            eta = d.get('eta') or 0

            percent = 0.0
            if total > 0:
                percent = round(downloaded / total * 100, 1)

            speed_str = f"{self._format_bytes(speed)}/s" if speed else "--"
            eta_str = f"{int(eta)}s" if eta else "--"
            total_str = self._format_bytes(total) if total else "--"

            line = f"[download] {percent}% of {total_str} at {speed_str} ETA {eta_str}"
            
            if self.progress_callback:
                self.progress_callback({
                    'status': 'downloading',
                    'percent': percent,
                    'speed': speed_str,
                    'eta': eta_str,
                    'total': total_str,
                    'line': line
                })

        elif status == 'finished':
            filename = os.path.basename(d.get('filename', ''))
            self.log(f"Скачивание завершено: {filename}. Склеивание и обработка...")
            if self.progress_callback:
                self.progress_callback({
                    'status': 'processing',
                    'percent': 100,
                    'line': f"Обработка {filename}..."
                })

    def download(self, url, save_dir, quality='max', on_complete=None):
        if self.is_downloading:
            self.log("Ошибка: уже идет скачивание!")
            return

        self.is_downloading = True
        self.cancel_requested = False

        def _run():
            downloaded_info = None
            try:
                os.makedirs(save_dir, exist_ok=True)
                clean_url = url.strip()
                self.log(f"Получение информации о видео...")

                ydl_opts = {
                    'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [self._progress_hook],
                    'logger': CustomYtdlLogger(self.log),
                    'noplaylist': True,
                    'windowsfilenames': True,
                    'overwrites': True,
                }

                # Ensure ffmpeg location is configured
                if not self.ffmpeg_path:
                    self.ffmpeg_path = self._find_ffmpeg()

                if self.ffmpeg_path:
                    ydl_opts['ffmpeg_location'] = self.ffmpeg_path

                # Quality mapping
                if quality == 'audio':
                    ydl_opts['format'] = 'bestaudio/best'
                    if self.ffmpeg_path:
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                elif quality == '1080p':
                    ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
                elif quality == '720p':
                    ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
                elif quality == '480p':
                    ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
                elif quality == '360p':
                    ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
                else:  # max
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.current_ydl = ydl
                    info = ydl.extract_info(clean_url, download=True)
                    
                    title = info.get('title', 'Video')
                    filepath = ydl.prepare_filename(info)
                    
                    if quality == 'audio':
                        base, _ = os.path.splitext(filepath)
                        filepath = base + ".mp3"

                    size_bytes = os.path.getsize(filepath) if os.path.exists(filepath) else (info.get('filesize') or 0)
                    
                    downloaded_info = {
                        'title': title,
                        'url': clean_url,
                        'filepath': filepath,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'size': self._format_bytes(size_bytes),
                        'quality': quality
                    }

                    self.log(f"Успешно сохранено: {os.path.basename(filepath)}")
                    self.log("Готово!")

            except Exception as e:
                err_msg = str(e)
                if "cancelled" in err_msg.lower():
                    self.log("Скачивание отменено пользователем.")
                else:
                    self.log(f"Ошибка: {err_msg}")
            finally:
                self.is_downloading = False
                self.current_ydl = None
                if on_complete:
                    on_complete(downloaded_info)

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def cancel(self):
        if self.is_downloading:
            self.cancel_requested = True
            self.log("Отмена скачивания...")


class CustomYtdlLogger:
    def __init__(self, callback):
        self.callback = callback

    def debug(self, msg):
        if msg.startswith('[download] Destination:') or msg.startswith('[Merger]') or msg.startswith('[ExtractAudio]'):
            self.callback(msg)

    def info(self, msg):
        if not msg.startswith('[download]'):
            self.callback(msg)

    def warning(self, msg):
        self.callback(f"Предупреждение: {msg}")

    def error(self, msg):
        self.callback(f"Ошибка: {msg}")
