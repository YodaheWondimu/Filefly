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
    """Updates the runtime status file with its numbers."""
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
    """Handles the movement and extraction of archive files."""
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
    """Returns a safe file path between a file and its destination."""
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
        # store normalized paths everywhere (normalized keys)
        self.moved_files = set()         # normalized paths we've moved (old or new)
        self.active_files = set()        # normalized paths currently being processed
        self.moved_files_ts = {}         # normalized old_path -> timestamp when we auto-moved it
        self.auto_mark_window = 30      # seconds within which deletes/moves are considered auto
        config = load_config()
        self.moved_files_count = 0
        self.ext_map = config["extensions"]
        self.temp_extensions = tuple(config["temp_extensions"])
        self.file_events = {}           # normalized path -> { event, timestamp }

    # ---------- Helpers ----------
    def _norm(self, path):
        """Normalize a filesystem path for stable dictionary/set keys."""
        if path is None:
            return None
        # abspath -> normpath -> normcase (Windows insensitive)
        return os.path.normcase(os.path.normpath(os.path.abspath(path)))

    def is_temp_path(self, path):
        """Return True if path ends with any known temporary extension."""
        if not path:
            return False
        lower = path.lower()
        return any(lower.endswith(ext) for ext in self.temp_extensions)

    def was_recent_auto(self, path):
        """Return True if normalized path was auto-handled recently."""
        n = self._norm(path)
        if not n:
            return False
        ts = self.moved_files_ts.get(n)
        return bool(ts and (time.time() - ts < self.auto_mark_window))

    def update_file_event(self, path, kind):
        """Record an 'auto' or 'manual' event for path (store normalized)."""
        n = self._norm(path)
        status = "auto" if kind == "auto" else "manual"
        self.file_events[n] = {"event": status, "timestamp": time.time()}
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {n} -> {status.upper()}")

    def mark_moved(self, old_path, new_path):
        """Remember that we moved a file (store normalized paths & timestamp)."""
        now = time.time()
        old_n = self._norm(old_path)
        new_n = self._norm(new_path)
        if old_n:
            self.moved_files.add(old_n)
            self.moved_files_ts[old_n] = now
        if new_n:
            self.moved_files.add(new_n)

    def mark_auto(self, path):
        """Mark a path as auto-handled (normalized)."""
        n = self._norm(path)
        if n:
            self.moved_files.add(n)
            self.moved_files_ts[n] = time.time()

    # ---------- Core file handling ----------
    def handle_file(self, path):
        """Wait for the file to stabilize and then move it to destination if applicable."""
        orig_path = os.path.abspath(path)
        norm_path = self._norm(orig_path)
        # Add to active set (normalized)
        self.active_files.add(norm_path)

        # Immediately ignore known temporary patterns
        if self.is_temp_path(orig_path):
            logger.info(f"Temp file still downloading: {orig_path}")
            # keep it in active_files if we want to track, but do not attempt to move
            return

        # If already acted on, skip
        if norm_path in self.moved_files:
            return

        # locate extension mapping
        suffixes = Path(orig_path).suffixes
        ext = "".join(suffixes).lower()
        if ext not in self.ext_map:
            return

        dest_folder = os.path.expanduser(self.ext_map[ext])
        os.makedirs(dest_folder, exist_ok=True)
        filename = os.path.basename(orig_path)
        new_dest_path = get_safe_path(dest_folder, filename)
        new_dest_norm = self._norm(new_dest_path)

        last_size = -1
        stable_count = 0
        waited = 0

        image_exts = {".jpg", ".jpeg", ".png"}
        is_image = ext in image_exts
        max_wait = 15 if is_image else 60

        # Wait loop for stabilization (same semantics as before)
        while waited < max_wait:
            if not os.path.exists(orig_path):
                time.sleep(0.5)
                waited += 0.5
                continue

            size = os.path.getsize(orig_path)

            if size < 1024 * 50:
                stable_count = max_wait

            if size == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = size

            logger.info(f"Checking {orig_path} (ext={ext}) size={size} last={last_size} stable_count={stable_count}...")

            if (is_image and stable_count >= 1) or (not is_image and stable_count >= 3):
                try:
                    if not os.path.exists(orig_path):
                        continue

                    # Move file
                    shutil.move(orig_path, new_dest_path)

                    # Mark event & bookkeeping using normalized keys
                    self.update_file_event(new_dest_path, "auto")
                    self.mark_moved(orig_path, new_dest_path)

                    logger.info(f"Moved {orig_path} -> {new_dest_path}")
                    self.moved_files_count += 1

                    # update global status (assumes update_status_file exists)
                    try:
                        update_status_file(self.moved_files_count)
                    except Exception:
                        logger.debug("update_status_file failed or is not available in this context.")

                    # remove from active set (normalized)
                    self.active_files.discard(norm_path)

                    # expire old timestamps (housekeeping)
                    now = time.time()
                    for f, ts in list(self.moved_files_ts.items()):
                        if now - ts > 3600:
                            self.moved_files_ts.pop(f, None)
                            self.moved_files.discard(f)

                    # Extract archives if needed
                    if ext in {".zip", ".7z", ".tar", ".tar.gz", ".tgz", ".tar.bz2"}:
                        handle_archive(new_dest_path, dest_folder)
                    return
                except Exception as e:
                    logger.error(f"Error moving {orig_path}: {e}")
                    return

            time.sleep(1)
            waited += 1

        logger.error(f"Failed to move {orig_path}: download couldn't stabilize after repeated attempts.")

    # ---------- Watchdog handlers ----------
    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path

        # Ignore temp-file creation messages (browser temp files)
        if self.is_temp_path(path):
            logger.info(f"Download started (temp): {path}")
            return

        logger.info(f"New file detected: {path}")
        # Only handle the file once: call handle_file()
        self.handle_file(path)

    def on_moved(self, event):
        if event.is_directory:
            return

        src = event.src_path
        dest = event.dest_path

        # If either side looks like a temp file, ignore (browser renames)
        if self.is_temp_path(src) or self.is_temp_path(dest):
            logger.info(f"Ignoring temp file move: {src} -> {dest}")
            return

        # If the destination is an archive or interesting extension, log it (non-critical)
        suffixes = Path(dest).suffixes
        ext = "".join(suffixes).lower()
        if ext in {".tar.gz", ".tar.bz2", ".tar.xz", ".zip", ".7z"} or (suffixes and suffixes[-1] in {".zip", ".7z"}):
            logger.info(f"Archive file detected: {dest}")

        # If we recently auto-handled this src path, treat this as auto and ignore manual logging
        if self.was_recent_auto(src) or self.was_recent_auto(dest):
            logger.info(f"Auto-move detected (handled by Filefly): {src} -> {dest}")
            return

        # Otherwise this appears to be a user/manual move/rename
        self.update_file_event(dest, "manual")
        logger.warning(f"File manually moved/renamed: {src} -> {dest}")

        # Process the new destination (one call only)
        self.handle_file(dest)

    def on_deleted(self, event):
        if event.is_directory:
            return

        path = event.src_path
        norm = self._norm(path)

        # Ignore temp-file deletions
        if self.is_temp_path(path):
            logger.info(f"Ignoring temp file delete: {path}")
            return

        # If delete corresponds to a recent auto-move we performed, ignore it
        if self.was_recent_auto(path) or norm in self.moved_files:
            logger.info(f"Ignoring auto-move delete event: {path}")
            # drop possible old timestamp
            self.moved_files_ts.pop(norm, None)
            return

        # If the file was being actively processed by us and was removed mid-process
        if norm in self.active_files:
            logger.warning(f"File manually removed mid-process: {path}")
            self.active_files.discard(norm)
            self.update_file_event(path, "manual")
            return

        # Otherwise this is an external manual delete/displacement
        logger.warning(f"File manually deleted or displaced: {path}")
        self.update_file_event(path, "manual")

    def on_modified(self, event):
        if event.is_directory:
            return
        path = event.src_path

        # Ignore temp file modifications
        if self.is_temp_path(path):
            return

        # If file is active, log update (normal)
        norm = self._norm(path)
        if norm in self.active_files:
            logger.info(f"File updating while downloading (active): {path}")
        else:
            # generic modification (someone edited or the OS changed metadata)
            logger.info(f"File modified: {path}")

def load_config():
    """Loads the configuration files for the management to base itself off of."""
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

def main():
    event_handler = DownloadsHandler()
    observer = Observer()

    for folder in watch_folders:
        os.makedirs(folder, exist_ok=True)
        observer.schedule(event_handler, path=folder, recursive=False)

    observer.start()
    logger.info(f"Now watching {watch_folders} for new files... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Filefly daemon stopped.")
        try:
            with open(STATUS_FILE, "r+") as f:
                data = json.load(f)
                data["active"] = False
                f.seek(0)
        except Exception:
            pass

    observer.join()

if __name__ == "__main__":
    main()