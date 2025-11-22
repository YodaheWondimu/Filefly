# Filefly
A self-learning file automation daemon that intelligently classifies and extracts downloaded files.
Works with dozens of file types and sizes to ensure compatiability while working with incoming files in real time.
It also includes a lightweight web dashboard for monitoring activity, viewing logs, and managing rules.

**Want to learn more? Check out the /logs branch to read weekly devlogs put in place before release.**

# Features

- Real-time monitoring of multiple folders
- Automatic extraction of ZIP, TAR, 7z, and more
- Self-learning event classification (auto vs manual)
- Browser-based dashboard (Flask)
- File routing based on extension rules
- Configurable folder mappings
- Detects manual deletes and moves
- Safe-move logic prevents overwrites
- Keeps a real-time runtime_status.json
- Logs everything to filefly.log

# Screenshots

## Terminal
![Terminal screenshot](assets/filefly_terminal.png)

# Web Dashboard
![Dashboard screenshot](assets/filefly_web_dashboard.png)

# How to Install

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

When Filefly runs for the first time, it generates:

```
~/.config/filefly/config.json   (or your packaged config)
```

Or if you're using your bundled config:

```
filefly/config.json
```

This file typically lives right next to main.py.
Users may edit this file to:
- add or remove watched folders
- map file extensions to destination directories
- define temporary extensions
- customize behavior

These file events follow the config files to know what to do, but the core logic can also "self-learn" if certain areas of your computer don't give off safe paths. It can also work its way around errors that may be thrown and pull all of its information gathered into a filefly.log file on startup.

Every config file has:
- a watch_folders section to store the folders on your computer that you want to watch
- an extensions folder to define file extensions and where you want to put files of those extensions
- a temp_extensions folder to store extensions of temporary files about to be renamed so Filefly can ignore them automatically
    - These temp extensions are files made by your browser every time you download a file off of them. They quickly rename themselves, however, once their full content is written into the file, which can trip up Filefly due to the potential of race conditions and the fact that you can't know what file type something is solely based on the temp extension. Filefly auto-stabilizes until these files fully write their info, then it's safe to move your files.

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

## Uninstalling

```
pip uninstall filefly
```

# Usage

Once the program is run, here's the process followed by the core logic:

- Filefly starts watching the folders defined in config.json
- When a file is detected:
    - it waits for the download to stabilize
    - determines its extension
    - moves it to the appropriate folder
    - logs the move in filefly.log
    - extracts archives when needed

# Directory Structure (inside Filefly/)

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

# Contributing and Development

Want to contribute to Filefly? Just clone this repository on your system and change up whatever's necessary:

```
git clone https://github.com/YodaheWondimu/Filefly.git
cd filefly
pip install -r requirements.txt
python -m filefly
```

# License

Filefly is released under the MIT License.
See `LICENSE` for more details.
