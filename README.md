# Filefly
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A real-time file automation daemon written in Python that monitors, classifies, and organizes files as they are downloaded.
Filefly combines rule-based routing with adaptive behavior to safely handle a wide range of file types.
Designed to handle real-world edge cases such as incomplete downloads, race conditions, and conflicting file operations.

**📓 Development logs documenting the full build process are available in the `logs` branch.**

## Features

### Core Functionality
- Real-time monitoring of multiple directories
- Rule-based file routing by extension
- Automatic archive extraction (ZIP, TAR, 7z)

### Reliability
- Safe-move logic to prevent overwrites
- Download stabilization to avoid partial file handling
- Detection of manual file moves and deletions

### Observability
- Real-time `runtime_status.json`
- Persistent logging via `filefly.log`
- Lightweight web dashboard (Flask)

## Screenshots

## Terminal
![Terminal screenshot](assets/filefly_terminal.png)

## Web Dashboard
![Dashboard screenshot](assets/filefly_web_dashboard.png)

## How to Install

## Install Filefly from PyPI (recommended)

Users are able to install Filefly with:

```
pip install filefly-files==0.1.0
```

All Python dependencies will install automatically.

## Running Filefly

### Option 1 — Run the daemon via terminal

After installation, Filefly should provide a command-line entry point:

```
filefly
```

This launches the background daemon and begins monitoring the configured folders.

### Option 2 — Run using Python directly

Exact equivalent to above:

```
python -m filefly
```

## Configuration

On first run, Filefly generates a configuration file:

- Linux/macOS: `~/.config/filefly/config.json`
- Local project: `filefly/config.json`

### Configuration Structure

`config.json`
```
{
    "watch_folders": ["~/Downloads"],
    "extensions": {
        ".zip": "~/Documents/Archives",
        ".pdf": "~/Documents/PDFs"
    },
    "temp_extensions": [".crdownload", ".part", ".tmp"]
}
```
Users may edit this file to customize behavior via three parameters: `watch_folders`, `extensions`, and `temp_extensions`.
watch_folders: directories on the watchlist
extensions: file types to reroute
temp_extensions: temporary download formats to ignore

Waiting for temporary files to stabilize before processing them prevents race conditions during downloads.

The `config.json` file typically lives right next to main.py.

The system can adapt to certain file behaviors over time and handle unexpected cases gracefully, using logged events to improve reliability.

File events are processed according to the rules defined in `config.json`.
If a file’s extension is recognized, it is routed to the configured destination; otherwise, it is ignored.
Filefly can work its way around errors that may be thrown, too.
All events and errors are recorded in `filefly.log` for traceability and debugging.

The extension routing works as a hand-in-hand communication with main.py and config.json.
When main.py detects a downloading file of a certain extension, it's sent to config.json to see if it's recognized.
If it's not, then the file is skipped over, but if it is, then main.py will find a matching extension and take the file to the desired folder based on its extension-folder dictionary in config.json.

### Example entry:

```
{
    "watch_folders": ["~/Downloads"],
    "extensions": {
        ".zip": "~/Documents/Archives",
        ".pdf": "~/Documents/PDFs"
    },
    "temp_extensions": [".crdownload", ".part", ".tmp"]
}
```

Accidentally deleted your config file? Don't worry - Filefly automatically regenerates a new one if it runs and doesn't start off with one.

## Optional: Start Filefly at login (OS-specific)
macOS

```
brew services restart filefly
```

(or a custom plist file)

Linux (systemd)

```
systemctl --user enable filefly
systemctl --user start filefly
```

Windows

Create a Task Scheduler task pointing to:

```
python -m filefly
```

## Verify installation

To ensure Filefly is installed correctly:

```
python -c "import filefly; print(filefly.__version__)"
```

## Upgrading

```
pip install --upgrade filefly-files
```

## Uninstalling

```
pip uninstall filefly-files
```

## How It Works

1. Filefly monitors configured directories
2. When a file appears:
   - waits for the file to stabilize
   - determines its extension
   - checks routing rules
3. If matched:
   - moves file to destination
   - extracts archives if needed
4. Logs all actions for traceability

## Project Structure

```
filefly/
├── static/
│   ├── script.js
│   └── styles.css
├── templates/
│   └── index.html
├── __init__.py
├── __main__.py
├── app.py
├── config.json
├── main.py
└── runtime_status.json
.gitignore
LICENSE
pyproject.toml
README.md
requirements.txt
```

## Contributing and Development
Want to contribute to Filefly? Just clone this repository on your system and make any necessary changes:

```
git clone https://github.com/YodaheWondimu/Filefly.git
cd filefly
pip install -r requirements.txt
python -m filefly
```

## License
Filefly is released under the MIT License.
See `LICENSE` for more details.
