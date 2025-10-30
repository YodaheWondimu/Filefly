# Made by Yodahe Wondimu
# This program is under the MIT license.
# I now present: Filefly.

"""Filefly: Automated file management and extraction daemon."""

# Imports essential libraries
import time
import shutil
import os
import zipfile
import py7zr # py7zr import preventing crashes on systems missing py7zr
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# Check whether or not the system using Filefly has py7zr imported
try:
    import py7zr
    HAS_PY7ZR = True
except ImportError:
    HAS_PY7ZR = False
    print("[Notice] py7zr is not installed. .7z archives will be skipped over if an archive extraction starts.")

# Global function to handle archive files
def handle_archive(archive_path, dest_folder):
    extract_folder = os.path.splitext(archive_path)[0]  # make subfolder with the archive file’s name
    os.makedirs(extract_folder, exist_ok=True)

    if archive_path.lower().endswith(".7z"):
        if HAS_PY7ZR:
            try:
                with py7zr.SevenZipFile(archive_path, mode='r') as archive: # Extracts via py7zr if the file is .7z and py7zr is on the system
                    archive.extractall(extract_folder)
                    print(f"Extracted {archive_path} -> {extract_folder}.")
            except Exception as e:
                print(f"[Error] Unexpected error extracting {archive_path}: {e}")
        else:
            print(f"[Error] {archive_path} cannot be extracted because its .7z file type cannot be supported at this time.\n"
                   "Install py7zr on this system in order to work with this file type.") # error message to advise users to install py7zr for .7z files
        return
    # Archives such as .tar.gz and .tar.bz2 are auto-extracted using shutil.unpack_archive(), differing from .7z files which require the py7zr library's extract method
    try:
        shutil.unpack_archive(archive_path, extract_folder) # Extracts archive folders after they're autosorted
        print(f"[Info] Extracted {archive_path} -> {extract_folder}.")
    except (shutil.ReadError, zipfile.BadZipFile):
        print(f"[Info] Invalid archive type: {archive_path}.")
    except Exception as e:
        print(f"[Info] Unexpected error extracting {archive_path}: {e}")

# Global function that can be used anywhere a collision-free file path is needed
def get_safe_path(dest_folder, filename):
    path = Path(filename)
    suffixes = path.suffixes            # e.g. ['.tar', '.gz']
    ext = "".join(suffixes).lower()     # ".tar.gz"
    name = path.stem                    # Filename without ALL suffixes; strips ALL suffixes, not just one

    new_dest_path = os.path.join(dest_folder, f"{name}{ext}")
    counter = 1

    # Track existing names to avoid infinite loops
    existing_files = set(os.listdir(dest_folder))

    while os.path.basename(new_dest_path) in existing_files:
        new_dest_path = os.path.join(dest_folder, f"{name}({counter}){ext}") # uses a counter to check for identically named files and rename the one being sorted accordingly
        counter += 1

    return new_dest_path
    # The new_dest_path declared and initialized in the while loop uses string concatenation to map suffixes to file types,
    # because certain file extensions such as .tar.gz have multiple dots.
    # The while loop's os.path.join() usage can be corroborated with ext's declaration and initialization earlier on in this method,
    # in the sense that both are joining matching suffixes together in order to properly associate files with these file types.

# DownloadsHandler class, which can detect certain activities being done in a specific folder. welcome to the heart of the program.
class DownloadsHandler(FileSystemEventHandler):
    """Definition:"""
    """Handles filesystem events in the watch folder, automatically sorting, moving, and extracting files."""

    """Methods Used:"""
    """__init__() - Defines the variables used within the class."""
    """mark_moved() - Marks file timestamps when they're moved to a new location"""
    """mark_auto() - Marks files when they're auto-moved by Filefly itself"""
    """is_temp() - Defines files as either temp or non-temp"""
    """handle_file() - The I/O's heartbeat, which methodically recognizes, moves and extracts files as they come into the watch folder"""
    """on_created() - Marks and notifies the console when files are created or brought into the watch folder via download"""
    """on_moved( - Marks and notifes the console when files are moved out of the watch folder or manually renamed/moved by the user"""
    """on_deleted() - Marks and distingushes to the console whether it was user deletions or auto-moves which moved the marked file(s) out of the watch folder"""
    """on_modified() - Marks and notifes the console when files inside the watch folder have their contents changed"""

    def __init__(self):
        super().__init__()
        self.moved_files = set()    # Track files we've already moved
        self.active_files = set()   # Tracks files currently being handled
        self.moved_files_ts = {}    # Tracks timestamp of auto-moved files
        self.auto_mark_window = 30  # Seconds within which a deletion is auto
        config = load_config()
        watch_folders = config["watch_folders"]
        self.ext_map = config["extensions"]
        self.temp_extensions = tuple(config["temp_extensions"])

    def mark_moved(self, old_path, new_path):
        now = time.time()
        self.moved_files.add(old_path)
        self.moved_files.add(new_path)
        self.moved_files_ts[old_path] = now # Only old path matters for deletion checks later

    def mark_auto(self, path):
        # Mark a file as auto-handled without moving it
        self.moved_files.add(path)
        self.moved_files_ts[path] = time.time()

    def is_temp(self, path):
        return path.lower().endswith(self.temp_extensions) # Returns whether or not the file is a temp file based on its extensions

    def handle_file(self, path):
        path = os.path.abspath(path)
        self.active_files.add(path)

        # Ignore temp/partial files
        # These files are ignored by the downloads handler because attempting to move them,
        # while they still are referred to as temporary, would lead to a race condition
        # because we would be moving a temp file before the download has enough time to get to renaming the file as its proper format.
        if path.lower().endswith(self.temp_extensions):
            print(f"[Info] Temp file still downloading: {path}")
            return
        
        # skip files that are already moved
        if path in self.moved_files:
            return

        suffixes = Path(path).suffixes  # e.g. ["archive", ".tar", ".gz"]
        ext = "".join(suffixes).lower() # ".tar.gz"
        if ext not in self.ext_map:
            return

        dest_folder = os.path.expanduser(self.ext_map[ext])
        os.makedirs(dest_folder, exist_ok=True)

        filename = os.path.basename(path)
        new_dest_path = get_safe_path(dest_folder, filename)
        
        # Wait for file to stabilize
        last_size = -1
        stable_count = 0
        waited = 0

        image_exts = {".jpg", ".jpeg", ".png"}
        is_image = ext in image_exts
        max_wait = 15 if is_image else 60

        while waited < max_wait: # Stable count loop to allow unstable files to finish downloading first; ensures we don't move files still being written to disk
            if not os.path.exists(path):
                time.sleep(0.5)
                waited += 0.5
                continue

            size = os.path.getsize(path)

            if size < 1024 * 50:  # smaller than 50 KB
                stable_count = max_wait  # Bypass wait loop (smaller files stabilize faster)
                # Note: smaller files like images typically complete downloading instantly without a considerable amount of temp file usage,
                # so we can skip the stabilization delay and start writing the file to the disk.
            if size == last_size:
                stable_count += 1
            else:
                stable_count = 0
                last_size = size
            
            print(f"[Info] Checking {path} (ext={ext}) size={size} last={last_size} stable_count={stable_count}...")

            if (is_image and stable_count >= 1) or (not is_image and stable_count >= 3): # Checks if stable ~3 seconds unless an image
                # Note: images do not need as much time to stabilize due to the less storage-intensive nature of their contents
                try:
                    if not os.path.exists(path):
                        continue
                    
                    shutil.move(path, new_dest_path)
                    self.mark_moved(path, new_dest_path)
                    print(f"Moved {path} -> {new_dest_path}")
                    self.active_files.discard(path)

                    now = time.time()
                    for f, ts in list(self.moved_files_ts.items()):
                        if now - ts > 3600:  # older than 1 hour
                            self.moved_files_ts.pop(f)
                            self.moved_files.discard(f)

                    if ext in {".zip", ".7z", ".tar", ".tar.gz", ".tgz", ".tar.bz2"}: # Is this file an archive type?
                        handle_archive(new_dest_path, dest_folder)
                    return
                except Exception as e:
                    print(f"[Error] Error moving {path}: {e}.")
                    return

            time.sleep(1)
            waited += 1

        print(f"[Error] Failed to move {path}: download couldn't stabilize after repeated attempts.")

    def on_created(self, event):
        if event.is_directory:
            return
        path = event.src_path
        if self.is_temp(path):
            print(f"[Info] Download started: {path}")
            return

        print(f"[Info] New file detected: {path}")
        self.handle_file(path)
        self.mark_auto(path)  # Mark auto even if file wasn’t moved

    def on_moved(self, event):
        if event.is_directory:
            return
        
        path = Path(event.dest_path)

        if path.name.startswith("~$") or any(s in {".tmp", ".temp"} for s in path.suffixes):
            print(f"[Info] Ignoring temp file move: {path}")
            return

        suffixes = path.suffixes
        ext = "".join(suffixes).lower()
        if ext in {".tar.gz", ".tar.bz2", ".tar.xz", ".zip", ".7z"} or (suffixes and suffixes[-1] in {".zip", ".7z"}):
            print(f"[Info] Archive file detected: {path}")

        if event.dest_path.lower().endswith(self.temp_extensions):
            # Only handle once the dest is the final (non-temp) file
            print(f"[Info] Temp file still downloading: {event.dest_path}")
            return
        
        src, dest = event.src_path, event.dest_path
        ts = self.moved_files_ts.get(src)
            
        # Was this move triggered by our handler?
        ts = self.moved_files_ts.get(event.src_path)
        if ts and time.time() - ts < self.auto_mark_window:
            print(f"[Info] Auto-move detected (handled by Filefly): {event.src_path} -> {event.dest_path}")
            return
        
        print(f"[Notice] File manually moved/renamed: {src} -> {dest}")
        self.handle_file(dest)  # Process just like an auto case
        
        print(f"[Info] Download renamed/finalized: {event.src_path} -> {event.dest_path}")
        self.handle_file(event.dest_path)
 
    def on_deleted(self, event):
        if event.is_directory:
            return

        ts = self.moved_files_ts.get(event.src_path)

        if ts and time.time() - ts < self.auto_mark_window:
            print(f"[Info] File auto-moved out of watch folder by Filefly (not deleted): {event.src_path}")
            del self.moved_files_ts[event.src_path]

        elif event.src_path in self.active_files:
            print(f"[Info] File manually removed mid-process: {event.src_path}")
            self.active_files.discard(event.src_path)

        else:
            print(f"[Notice] File manually deleted or displaced: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            if not event.src_path.lower().endswith(self.temp_extensions):
                print(f"[Info] File updating while downloading: {event.src_path}")

def load_config():
    """Load configuration from backend/config.json, creating defaults if missing."""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(backend_dir, "config.json")

    default_config = {
        "watch_folders": ["~/Downloads", "~/Documents"]
    }

    # If config doesn't exist, create one with default settings
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        print("[Info] Created default config.json file with default folders.")

    # Load config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Expand ~ for each path and return
    config["watch_folders"] = [
        os.path.expanduser(path) for path in config.get("watch_folders", [])
    ]
    return config

config = load_config()
watch_folders = config["watch_folders"]

# Choosing the downloads path and observer
watch_folders = [os.path.expanduser(path) for path in config.get("watch_folders", ["~/Downloads", "~/Documents"])] # Default watch directories listed; can be expanded in config.json
event_handler = DownloadsHandler()
observer = Observer()
for folder in watch_folders:
    os.makedirs(folder, exist_ok=True)  # Create folder if missing
    observer.schedule(event_handler, path=folder, recursive=True)

observer.start()
print(f"[Info] Now watching {watch_folders} for new files...\n(Ctrl+C to stop)")

# Try loop to wait until program interrupted by intentional KeyboardInterrupt
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()