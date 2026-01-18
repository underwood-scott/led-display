
from flask import Flask, render_template, request, redirect, url_for
from multiprocessing import Process
import os
import signal

app = Flask(__name__)

# Default teams (can be changed via web)
NFL_TEAMS = ['Green Bay Packers', 'Chicago Bears']
NBA_TEAMS = ['Milwaukee Bucks', 'Los Angeles Lakers', 'Orlando Magic']
NCAAFB_TEAMS = ['Wisconsin Badgers']
NCAABB_TEAMS = ['Wisconsin Badgers', 'Marquette Golden Eagles']
MLB_TEAMS = ['Milwaukee Brewers', 'Chicago Cubs']

display_process = None
display_type = None


@app.route("/", methods=["GET"])
def index():
    status = f"Current: {display_type or 'None'}"
    return render_template(
        "index.html",
        nfl_teams=", ".join(NFL_TEAMS),
        nba_teams=", ".join(NBA_TEAMS),
        mlb_teams=", ".join(MLB_TEAMS),
        ncaafb_teams=", ".join(NCAAFB_TEAMS),
        ncaabb_teams=", ".join(NCAABB_TEAMS),
        status=status
    )


@app.route("/set_teams", methods=["POST"])
def set_teams():
    global NFL_TEAMS, NBA_TEAMS, MLB_TEAMS, NCAAFB_TEAMS, NCAABB_TEAMS
    NFL_TEAMS = [t.strip() for t in request.form.get("nfl", "").split(",") if t.strip()]
    NBA_TEAMS = [t.strip() for t in request.form.get("nba", "").split(",") if t.strip()]
    MLB_TEAMS = [t.strip() for t in request.form.get("mlb", "").split(",") if t.strip()]
    NCAAFB_TEAMS = [t.strip() for t in request.form.get("ncaafb", "").split(",") if t.strip()]
    NCAABB_TEAMS = [t.strip() for t in request.form.get("ncaabb", "").split(",") if t.strip()]
    return redirect(url_for("index"))


def stop_display_process():
    global display_process, display_type
    if display_process and display_process.is_alive():
        os.kill(display_process.pid, signal.SIGTERM)
        display_process.join(timeout=2)
    display_process = None
    display_type = None


@app.route("/start_sports_display", methods=["POST"])
def start_sports_display():
    global display_process, display_type
    stop_display_process()

    from sports_display.app import SportsDisplay
    display_process = Process(target=SportsDisplay(NFL_TEAMS, NCAAFB_TEAMS, NBA_TEAMS, NCAABB_TEAMS, MLB_TEAMS).run)
    display_process.start()
    display_type = "Sports Display"
    return redirect(url_for("index"))


@app.route("/start_metro_display", methods=["POST"])
def start_metro_display():
    global display_process, display_type
    stop_display_process()
    # Try to import MetroDisplay if available

    MetroDisplay = None
    if MetroDisplay:
        display_process = Process(target='metro_display/run.sh')
        display_process.start()
        display_type = "Metro Display"
    return redirect(url_for("index"))


@app.route("/stop_display", methods=["POST"])
def stop_display():
    stop_display_process()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
