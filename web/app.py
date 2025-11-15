# Made by Yodahe Wondimu
# Welcome to the backend of Filefly.
# The stage sets, and the curtains are pulled aside...

from flask import Flask, jsonify, render_template, send_from_directory
import threading
import logging
import time
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
status_file = os.path.join(base_dir, "runtime_status.json") # Defines runtime_status.json as the single source of truth for the status

app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, "static"),
    template_folder=os.path.join(base_dir, "templates")
)

def load_config():
    config_path = os.path.join(base_dir, "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Config file missing at {config_path}. Using default watch folders.")
        return {"watch_folders": ["~/Downloads", "~/Documents"]}

def read_status():
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            return json.load(f)
    return {"active": False, "watched_folders": [], "moved_files": 0}

# Dumps the status into the status_file (runtime_status.json)
def write_status(data):
    with open(status_file, "w") as f:
        json.dump(data, f, indent=4)

# Initialize the JSON file if it doesn't exist yet
if not os.path.exists(status_file):
    initial_status = {
        "active": True,
        "watched_folders": load_config().get("watch_folders", []),
        "moved_files": 0
    }
    write_status(initial_status)

@app.route("/")
def home():
    return render_template("index.html", status=read_status()) # Imports the render template in index.html

@app.route("/status")
def status():
    return jsonify(read_status())

@app.route("/reload")
def reload_config():
    config = load_config()
    status = read_status()
    status["watched_folders"] = config.get("watch_folders", [])
    write_status(status) # Writes the status as it was made in app.py, effectively reloading the config
    return jsonify({"message": "Config reloaded!", "new_config": config})

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

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
        status = read_status()
        status["active"] = False
        write_status(status)