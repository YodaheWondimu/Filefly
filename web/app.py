# Made by Yodahe Wondimu
# Welcome to the backend of Filefly.
# The stage sets, and the curtains are pulled aside...

from flask import Flask, jsonify, render_template, send_from_directory
import threading
import time
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# Create Flask app
app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, "static"),
    template_folder=os.path.join(base_dir, "templates")
)


# Load config file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[Notice] config.json not found, using default watch folders (Downloads & Documents)")
        return {"watch_folders": ["~/Downloads", "~/Documents"]}

config = load_config()

status_file = os.path.join(os.path.dirname(__file__), "runtime_status.json")

def get_live_status():
    status_file = os.path.join(os.path.dirname(__file__), "runtime_status.json")
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            return json.load(f)
    else:
        return {"active": False, "watched_folders": [], "moved_files": 0}

# Runtime status
filefly_status = {
    "active": True,
    "watched_folders": config.get("watch_folders", []),
    "moved_files": 0
}

# Initialize runtime_status.json if missing
if not os.path.exists(status_file):
    with open(status_file, "w") as f:
        json.dump(filefly_status, f, indent=4)

# ----- ROUTES -----

@app.route("/")
def home():
    """Serve the main HTML dashboard."""
    return render_template("index.html", status=filefly_status)

@app.route("/status")
def status():
    """Return current daemon status (JSON)."""
    return jsonify(filefly_status)

@app.route("/reload")
def reload_config():
    """Reload config.json."""
    global config, filefly_status
    config = load_config()
    filefly_status["watched_folders"] = config.get("watch_folders", [])
    return jsonify({"message": "Config reloaded!", "new_config": config})

# Optional: serve CSS/JS manually if needed (Flask usually does this automatically)
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ----- FLASK THREADING -----

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Info] Filefly backend shutting down gracefully...")