# Made by Yodahe Wondimu
# Welcome to the backend of Filefly.
# The stage sets, and the curtains are pulled aside...

# Imports essential libraries
from flask import Flask, jsonify
import threading
import time
import json
import os

app = Flask(__name__) # Creates the app - the start of it all

# Helper method based on the config loading file in main.py
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[Notice] config.json not found, using default watch folders (Downloads & Documents)")
        return {"watch_folders": ["~/Downloads", "~/Documents"]}

config = load_config()

# Represents the Filefly runtime status
filefly_status = {
    "active": True,
    "watched_folders": config.get("watch_folders", []),
    "moved_files": 23
}

@app.route("/")
def home():
    """Returns a basic landing page."""
    return "<h1>Filefly API</h1><p>Welcome to your file automation backend!</p>"

@app.route("/status")
def status():
    """Returns the current status of the Filefly watcher."""
    return jsonify(filefly_status)

@app.route("/reload")
def reload_config():
    global config, filefly_status
    config = load_config()
    filefly_status["watched_folders"] = config.get("watch_folders", [])
    return jsonify({"message": "Config reloaded!", "new_config": config})

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Simulates the daemon forever loop
    while True:
        try:
            while True:
                time.sleep(1)  # simulate the daemon staying alive
        except KeyboardInterrupt:
            print("\n[Info] Filefly backend shutting down gracefully...")
            # this can also stop observers or save logs here later