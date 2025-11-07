# Made by Yodahe Wondimu
# This program is under the MIT license.
# I now present: Filefly.

"""Filefly: Automated file management and extraction daemon."""

import time
import shutil
import os
import zipfile
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("filefly.log"),  # saves logs to a file
        logging.StreamHandler()              # also prints to console
    ]
)
logger = logging.getLogger(__name__)

# Check whether or not the system using Filefly has py7zr imported
try:
    import py7zr
    HAS_PY7ZR = True
except ImportError:
    HAS_PY7ZR = False
    logger.warning("py7zr is not installed. .7z archives will be skipped over during archive extraction.")

STATUS_FILE = os.path.join(os.path.dirname(__file__), "runtime_status.json")

def update_status_file(moved_files_count):
    status_data = {
        "active": True,
        "watched_folders": watch_folders,
        "moved_files": moved_files_count
    }
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status_data, f, indent=4)
    except Exception as e:
        logger.warning(f"Could not update runtime_status.json: {e}")

# Global function to handle archive files
def handle_archive(archive_path, dest_folder):
    extract_folder = os.path.splitext(archive_path)[0]
    os.makedirs(extract_folder, exist_ok=True)

    if archive_path.lower().endswith(".7z"):
        if HAS_PY7ZR:
            try:
                with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                    archive.extractall(extract_folder)
                    logger.info(f"Extracted {archive_path} -> {extract_folder}")
            except Exception as e:
                logger.error(f"Unexpected error extracting {archive_path}: {e}")
        else:
            logger.error(f"{archive_path} cannot be extracted because its .7z file type is not supported. "
                         f"Install py7zr on this system to enable support.")
        return

    try:
        shutil.unpack_archive(archive_path, extract_folder)
        logger.info(f"Extracted {archive_path} -> {extract_folder}")
    except (shutil.ReadError, zipfile.BadZipFile):
        logger.warning(f"Invalid archive type: {archive_path}")
    except Exception as e:
        logger.error(f"Unexpected error extracting {archive_path}: {e}")

def get_safe_path(dest_folder, filename):
    path = Path(filename)
    suffixes = path.suffixes
    ext = "".join(suffixes).lower()
    name = path.name[:-len(ext)] if ext else path.name

    counter = 0
    base_files = {f.lower() for f in os.listdir(dest_folder)}

    if os.path.dirname(os.path.abspath(filename)) == os.path.abspath(dest_folder):
        base_files.discard(os.path.basename(filename).lower())

    while True:
        suffix = f"({counter})" if counter > 0 else ""
        new_name = f"{name}{suffix}{ext}"
        safe_path = os.path.join(dest_folder, new_name)
        try:
            with open(safe_path, "xb") as f:
                pass
            os.remove(safe_path)
            return safe_path
        except FileExistsError:
            counter += 1
            continue

class DownloadsHandler(FileSystemEventHandler):
    """Handles filesystem events in the watch folder, automatically sorting, moving, and extracting files."""

    def __init__(self):
        super().__init__()
        self.moved_files = set()
        self.active_files = set()
        self.moved_files_ts = {}
        self.auto_mark_window = 30
        config = load_config()
        self.moved_files_count = 0
        self.ext_map = config["extensions"]
        self.temp_extensions = tuple(config["temp_extensions"])

    def mark_moved(self, old_path, new_path):
        now = time.time()
        self.moved_files.add(old_path)
        self.moved_files.add(new_path)
        self.moved_files_ts[old_path] = now

    def mark_auto(self, path):
        self.moved_files.add(path)
        self.moved_files_ts[path] = time.time()

    def is_temp(self, path):
        return path.lower().endswith(self.temp_extensions)

    def handle_file(self, path):
        path = os.path.abspath(path)
        self.active_files.add(path)

        if path.lower().endswith(self.temp_extensions):
            logger.info(f"Temp file still downloading: {path}")
            return

        if path in self.moved_files:
            return

        suffixes = Path(path).suffixes
        ext = "".join(suffixes).lower()
        if ext not in self.ext_map:
            return

        dest_folder = os.path.expanduser(self.ext_map[ext])
        os.makedirs(dest_folder, exist_ok=True)
        filename = os.path.basename(path)
        new_dest_path = get_safe_path(dest_folder, filename)

        last_size = -1
        stable_count = 0
        waited = 0

        image_exts = {".jpg", ".jpeg", ".png"}
        is_image = ext in image_exts
        max_wait = 15 if is_image else 60

        while waited < max_wait:
            if not os.path.exists(path):
                time.sleep(0.5)
                waited += 0.5
                continue

            size = os.path.getsize(path)

            if size < 1024 * 50:
                stable_count = max_wait

            if size == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = size

            logger.info(f"Checking {path} (ext={ext}) size={size} last={last_size} stable_count={stable_count}...")

            if (is_image and stable_count >= 1) or (not is_image and stable_count >= 3):
                try:
                    if not os.path.exists(path):
                        continue

                    shutil.move(path, new_dest_path)
                    self.mark_moved(path, new_dest_path)
                    logger.info(f"Moved {path} -> {new_dest_path}")
                    self.moved_files_count += 1
                    update_status_file(self.moved_files_count)
                    self.active_files.discard(path)

                    now = time.time()
                    for f, ts in list(self.moved_files_ts.items()):
                        if now - ts > 3600:
                            self.moved_files_ts.pop(f)
                            self.moved_files.discard(f)

                    if ext in {".zip", ".7z", ".tar", ".tar.gz", ".tgz", ".tar.bz2"}:
                        handle_archive(new_dest_path, dest_folder)
                    return
                except Exception as e:
                    logger.error(f"Error moving {path}: {e}")
                    return

            time.sleep(1)
            waited += 1

        logger.error(f"Failed to move {path}: download couldn't stabilize after repeated attempts.")

    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path
        if self.is_temp(path):
            logger.info(f"Download started: {path}")
            return

        logger.info(f"New file detected: {path}")
        self.handle_file(path)
        self.mark_auto(path)

    def on_moved(self, event):
        if event.is_directory:
            return

        path = Path(event.dest_path)
        if path.name.startswith("~$") or any(s in {".tmp", ".temp"} for s in path.suffixes):
            logger.info(f"Ignoring temp file move: {path}")
            return

        suffixes = path.suffixes
        ext = "".join(suffixes).lower()
        if ext in {".tar.gz", ".tar.bz2", ".tar.xz", ".zip", ".7z"} or (suffixes and suffixes[-1] in {".zip", ".7z"}):
            logger.info(f"Archive file detected: {path}")

        if event.dest_path.lower().endswith(self.temp_extensions):
            logger.info(f"Temp file still downloading: {event.dest_path}")
            return

        src, dest = event.src_path, event.dest_path
        ts = self.moved_files_ts.get(src)

        if ts and time.time() - ts < self.auto_mark_window:
            logger.info(f"Auto-move detected (handled by Filefly): {src} -> {dest}")
            return

        logger.warning(f"File manually moved/renamed: {src} -> {dest}")
        self.handle_file(dest)

        logger.info(f"Download renamed/finalized: {src} -> {dest}")
        self.handle_file(dest)

    def on_deleted(self, event):
        if event.is_directory:
            return

        ts = self.moved_files_ts.get(event.src_path)

        if ts and time.time() - ts < self.auto_mark_window:
            logger.info(f"File auto-moved out of watch folder by Filefly (not deleted): {event.src_path}")
            del self.moved_files_ts[event.src_path]

        elif event.src_path in self.active_files:
            logger.warning(f"File manually removed mid-process: {event.src_path}")
            self.active_files.discard(event.src_path)
        else:
            logger.warning(f"File manually deleted or displaced: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory and not event.src_path.lower().endswith(self.temp_extensions):
            logger.info(f"File updating while downloading: {event.src_path}")

def load_config():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(backend_dir, "config.json")

    default_config = {
        "watch_folders": ["~/Downloads", "~/Documents"],
        "extensions": {
            ".zip": "~/Documents/Archives",
            ".pdf": "~/Documents/PDFs",
            ".jpg": "~/Pictures",
            ".png": "~/Pictures",
            ".txt": "~/Documents/TextFiles"
        },
        "temp_extensions": [".crdownload", ".part", ".tmp"]
    }

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        logger.info("Created default config.json file with default folders.")

    with open(config_path, "r") as f:
        config = json.load(f)

    config["watch_folders"] = [
        os.path.expanduser(path) for path in config.get("watch_folders", [])
    ]
    return config

config = load_config()
watch_folders = config["watch_folders"]

event_handler = DownloadsHandler()
observer = Observer()
for folder in watch_folders:
    os.makedirs(folder, exist_ok=True)
    observer.schedule(event_handler, path=folder, recursive=False)

observer.start()
logger.info(f"Now watching {watch_folders} for new files... (Ctrl+C to stop)")
update_status_file(0)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    logger.info("Stopping Filefly daemon...")
    update_status_file(event_handler.moved_files_count)
    with open(STATUS_FILE, "r+") as f:
        data = json.load(f)
        data["active"] = False
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

observer.join()