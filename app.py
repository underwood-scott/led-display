from flask import Flask
import subprocess
import os
import signal

app = Flask(__name__)
process = None

@app.route('/on')
def turn_on():
    global process
    if process is None:
        # Replace 'metro.py' with the actual entry script in your repo
        # Use 'sudo' because the LED matrix library requires root
        process = subprocess.Popen(["sudo", "metro-display/run.sh"], preexec_fn=os.setsid)
        return "Display turned ON"
    return "Display is already ON"

@app.route('/off')
def turn_off():
    global process
    if process is not None:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process = None
        return "Display turned OFF"
    return "Display is already OFF"

if __name__ == '__main__':
    # Listen on all network interfaces so your phone can see it
    app.run(host='0.0.0.0', port=5000)
