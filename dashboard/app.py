import os
import json
import subprocess
import threading
import time
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timezone

app = Flask(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.getenv('COWRIE_LOG_PATH', os.path.join(BASE_DIR, '../cowrie/logs/cowrie.json'))
BLOCKED_IPS_FILE = os.path.join(BASE_DIR, 'blocked_ips.json')

# Suspicious activity triggers
SUSPICIOUS_KEYWORDS = ['curl', 'wget', 'bash', 'base64', 'nc', 'netcat', 'python', 'perl', 'ruby', 'gcc', 'chmod +x']

def load_blocked_ips():
    if os.path.exists(BLOCKED_IPS_FILE):
        try:
            with open(BLOCKED_IPS_FILE, 'r') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} blocked IPs: {data}")
                return set(data)
        except Exception as e:
            print(f"Error loading blocklist: {e}")
            return set()
    return set()

def save_blocked_ips(ips):
    try:
        with open(BLOCKED_IPS_FILE, 'w') as f:
            json.dump(list(ips), f)
        print(f"Saved blocklist to {BLOCKED_IPS_FILE}: {list(ips)}")
    except Exception as e:
        print(f"Error saving blocklist: {e}")

BLOCKED_IPS = load_blocked_ips()

def terminate_session(ip):
    """Forcefully logs out all intruders by restarting the honeypot container"""
    try:
        print(f"ATTEMPTING TERMINATION for IP: {ip}")
        result = subprocess.run(['docker', 'restart', 'cowrie-honeypot'], capture_output=True, text=True, check=True)
        print(f"DOCKER RESTART SUCCESS: {result.stdout}")
        print(f"TERMINATED: Forcefully dropped all sessions due to block list update/violation by {ip}.")
    except subprocess.CalledProcessError as e:
        print(f"DOCKER RESTART FAILED: {e.stderr}")
    except Exception as e:
        print(f"Error terminating session: {e}")

def analyze_event(entry):
    """Classifies an event and returns a risk score (0-100)"""
    score = 0
    tags = []
    
    eventid = entry.get('eventid', '')
    cmd = entry.get('input', '')
    
    if eventid == 'cowrie.login.success':
        score = 40
        tags.append('auth_success')
    elif eventid == 'cowrie.login.failed':
        score = 10
        tags.append('brute_force_attempt')
    
    if cmd:
        score += 20
        tags.append('shell_interaction')
        if any(keyword in cmd for keyword in SUSPICIOUS_KEYWORDS):
            score += 50
            tags.append('suspicious_tool_execution')
            
    if eventid == 'cowrie.session.connect':
        tags.append('connection_start')
        
    return min(score, 100), tags

def get_honeypot_data():
    global BLOCKED_IPS
    sessions = {}
    logs = []
    unique_ips = {}
    incidents = []
    
    if not os.path.exists(LOG_FILE):
        return {"active_sessions": 0, "total_events": 0, "unique_ips": 0, "logs": [], "incidents": []}

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    entry = json.loads(line)
                    ip = entry.get('src_ip')
                    if not ip: continue
                    
                    # Risk Assessment
                    risk_score, tags = analyze_event(entry)
                    entry['risk_score'] = risk_score
                    entry['tags'] = tags
                    
                    logs.append(entry)
                    
                    # IP Tracking
                    if ip not in unique_ips:
                        unique_ips[ip] = {"first_seen": entry['timestamp'], "events": 0, "max_risk": 0}
                    unique_ips[ip]['events'] += 1
                    unique_ips[ip]['max_risk'] = max(unique_ips[ip]['max_risk'], risk_score)
                    unique_ips[ip]['last_seen'] = entry['timestamp']
                    unique_ips[ip]['is_blocked'] = ip in BLOCKED_IPS

                    # Auto-block logic
                    event_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    time_diff = (now - event_time).total_seconds()
                    
                    eventid = entry.get('eventid')
                    
                    # Trigger block/termination if:
                    # 1. High risk event detected RECENTLY (within 120s for background processing)
                    if risk_score >= 70 and ip not in BLOCKED_IPS and time_diff < 120:
                        print(f"!!! BLOCK TRIGGERED !!! IP: {ip}, Cmd: {entry.get('input')}, TimeDiff: {time_diff}s")
                        BLOCKED_IPS.add(ip)
                        save_blocked_ips(BLOCKED_IPS)
                        unique_ips[ip]['is_blocked'] = True
                        terminate_session(ip)
                    
                    # 2. Blocked IP attempts to reconnect recently
                    elif ip in BLOCKED_IPS and eventid == 'cowrie.session.connect' and time_diff < 30:
                        print(f"!!! RECONNECT BLOCK !!! IP: {ip}, TimeDiff: {time_diff}s")
                        terminate_session(ip)

                    # Session Tracking
                    sid = entry.get('session')
                    if eventid == 'cowrie.session.connect':
                        sessions[sid] = entry
                    elif eventid == 'cowrie.session.closed':
                        if sid in sessions:
                            del sessions[sid]
                            
                except json.JSONDecodeError:
                    print(f"JSON Decode Error in log line: {line}")
                    continue
                except Exception as e:
                    print(f"Error processing log entry: {e} for line: {line}")
    except Exception as e:
        print(f"Error reading log file: {e}")

    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for ip, data in unique_ips.items():
        if data['max_risk'] >= 30 or data['is_blocked']:
            incidents.append({"ip": ip, **data})
    
    incidents.sort(key=lambda x: x['max_risk'], reverse=True)

    return {
        "active_sessions": len(sessions),
        "total_events": len(logs),
        "unique_ips": len(unique_ips),
        "logs": logs[:100],
        "incidents": incidents
    }

def background_monitor():
    """Background thread to process logs and block IPs even without UI activity"""
    print("Background monitor started.")
    while True:
        try:
            get_honeypot_data()
        except Exception as e:
            print(f"Monitor error: {e}")
        time.sleep(5)

# Start background monitor
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    return jsonify(get_honeypot_data())

@app.route('/api/block', methods=['POST'])
def block_ip():
    data = request.get_json()
    ip = data.get('ip') if data else None
    if ip:
        BLOCKED_IPS.add(ip)
        save_blocked_ips(BLOCKED_IPS)
        terminate_session(ip)
        return jsonify({"status": "success", "message": f"IP {ip} blocked"})
    return jsonify({"status": "error", "message": "No IP provided"}), 400

@app.route('/api/unblock', methods=['POST'])
def unblock_ip():
    data = request.get_json()
    ip = data.get('ip') if data else None
    if ip:
        if ip in BLOCKED_IPS:
            BLOCKED_IPS.remove(ip)
            save_blocked_ips(BLOCKED_IPS)
        return jsonify({"status": "success", "message": f"IP {ip} unblocked"})
    return jsonify({"status": "error", "message": "No IP provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False) # Disable debug to prevent double thread start
