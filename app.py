
from flask import Flask, render_template, request, redirect, url_for
from multiprocessing import Process
import json
import logging
import subprocess
import os
import signal

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default teams (can be changed via web)
DEFAULT_TEAMS = {
    'nfl': ['Green Bay Packers'],
    'nba': ['Milwaukee Bucks'],
    'ncaafb': ['Wisconsin Badgers'],
    'ncaabb': ['Wisconsin Badgers'],
    'mlb': ['Milwaukee Brewers']
}

TEAMS_FILE = '/tmp/sports_teams.json'

display_process = None
display_type = None
PID_FILE = '/tmp/display_pid.txt'
TYPE_FILE = '/tmp/display_type.txt'


@app.route("/", methods=["GET"])
def index():
    # Ensure teams file exists with defaults
    if not os.path.exists(TEAMS_FILE):
        with open(TEAMS_FILE, 'w') as f:
            json.dump(DEFAULT_TEAMS, f)
    
    # Load teams from file
    with open(TEAMS_FILE, 'r') as f:
        teams_data = json.load(f)
    
    if os.path.exists(TYPE_FILE):
        with open(TYPE_FILE, 'r') as f:
            current_type = f.read().strip()
    else:
        current_type = "None"
    
    if current_type == "Sports Display":
        mode = "sports"
    elif current_type == "Metro Display":
        mode = "metro"
    else:
        mode = "off"
    
    status = f"Display: {current_type}"
    return render_template(
        "index.html",
        nfl_teams=teams_data['nfl'],
        nba_teams=teams_data['nba'],
        mlb_teams=teams_data['mlb'],
        ncaafb_teams=teams_data['ncaafb'],
        ncaabb_teams=teams_data['ncaabb'],
        mode=mode,
        status=status
    )


@app.route("/set_mode", methods=["POST"])
def set_mode():
    mode = request.form.get("mode")
    if mode == "sports":
        return start_sports_display()
    elif mode == "metro":
        return start_metro_display()
    elif mode == "off":
        return stop_display()
    return redirect(url_for("index"))


@app.route("/set_teams", methods=["POST"])
def set_teams():
    teams_data = {
        'nfl': request.form.getlist("nfl"),
        'nba': request.form.getlist("nba"),
        'mlb': request.form.getlist("mlb"),
        'ncaafb': request.form.getlist("ncaafb"),
        'ncaabb': request.form.getlist("ncaabb")
    }
    with open(TEAMS_FILE, 'w') as f:
        json.dump(teams_data, f)
    
    # If display is running, restart it to pick up new teams
    if os.path.exists(TYPE_FILE):
        with open(TYPE_FILE, 'r') as f:
            current_type = f.read().strip()
        if current_type == "Sports Display":
            stop_display_process()
            start_sports_display()
        elif current_type == "Metro Display":
            stop_display_process()
            start_metro_display()
    
    return redirect(url_for("index"))


def stop_display_process():
    global display_process, display_type
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid_str = f.read().strip()
            if pid_str:
                try:
                    pid = int(pid_str)
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    logger.info(f"Sent SIGTERM to process group of PID: {pid}")
                except (ValueError, ProcessLookupError, OSError):
                    logger.warning(f"PID {pid_str} not valid or process group already dead")
        os.remove(PID_FILE)
    else:
        logger.info("No PID file found; no active display process to stop.")
    if os.path.exists(TYPE_FILE):
        os.remove(TYPE_FILE)
    display_process = None
    display_type = None


@app.route("/start_sports_display", methods=["POST"])
def start_sports_display():
    global display_process, display_type
    stop_display_process()
    logger.info("Starting Sports Display process...")
    try:
        display_process = subprocess.Popen(['sudo', './sports_display/run.sh'], preexec_fn=os.setsid)
        with open(PID_FILE, 'w') as f:
            f.write(str(display_process.pid))
        with open(TYPE_FILE, 'w') as f:
            f.write("Sports Display")
        display_type = "Sports Display"
        logger.info(f"Sports Display process started. PID: {display_process.pid}")
    except Exception as e:
        logger.error(f"Failed to start Sports Display: {e}")
        display_type = "Error"
    return redirect(url_for("index"))


@app.route("/start_metro_display", methods=["POST"])
def start_metro_display():
    global display_process, display_type
    stop_display_process()
    logger.info("Starting Metro Display process...")
    try:
        display_process = subprocess.Popen(['sudo', './metro_display/run.sh'], preexec_fn=os.setsid)
        with open(PID_FILE, 'w') as f:
            f.write(str(display_process.pid))
        with open(TYPE_FILE, 'w') as f:
            f.write("Metro Display")
        display_type = "Metro Display"
        logger.info(f"Metro Display process started. PID: {display_process.pid}, Alive: {display_process.poll() is None}")
    except Exception as e:
        logger.error(f"Failed to start Metro Display: {e}")
        display_type = "Error"
    return redirect(url_for("index"))


@app.route("/stop_display", methods=["POST"])
def stop_display():
    logger.info("Stop display requested.")
    stop_display_process()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
