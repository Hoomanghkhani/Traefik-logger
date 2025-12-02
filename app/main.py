import json
import sqlite3
import time
import os
import threading
from datetime import datetime, timedelta
from dateutil import parser
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
DB_PATH = 'logs.db'
LOG_FILE = os.environ.get('LOG_FILE_PATH', '/var/log/traefik/access.log')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME,
                  service TEXT,
                  client_ip TEXT,
                  method TEXT,
                  path TEXT,
                  status INTEGER,
                  duration INTEGER,
                  raw TEXT)''')
    conn.commit()
    conn.close()

def parse_log_line(line):
    try:
        data = json.loads(line)
        ts_str = data.get('StartUTC') or data.get('time')
        ts = parser.parse(ts_str) if ts_str else datetime.utcnow()
        
        return {
            'timestamp': ts,
            'service': data.get('RouterName', 'unknown'),
            'client_ip': data.get('ClientHost', 'unknown'),
            'method': data.get('RequestMethod', 'unknown'),
            'path': data.get('RequestPath', 'unknown'),
            'status': int(data.get('DownstreamStatus', 0)),
            'duration': int(data.get('Duration', 0)) / 1000000, # Convert ns to ms
            'raw': line
        }
    except Exception as e:
        # print(f"Error parsing line: {e}")
        return None

def log_reader():
    print(f"Watching log file: {LOG_FILE}")
    while not os.path.exists(LOG_FILE):
        time.sleep(2)
        print(f"Waiting for log file: {LOG_FILE}")

    f = open(LOG_FILE, 'r')
    f.seek(0, 2) # Start from end
    
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        parsed = parse_log_line(line)
        if parsed:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO requests (timestamp, service, client_ip, method, path, status, duration, raw) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (parsed['timestamp'], parsed['service'], parsed['client_ip'], parsed['method'], parsed['path'], parsed['status'], parsed['duration'], parsed['raw']))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"DB Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    
    query = "SELECT timestamp, status, duration, service FROM requests WHERE 1=1"
    params = []
    
    if start_str:
        query += " AND timestamp >= ?"
        params.append(parser.parse(start_str))
    if end_str:
        query += " AND timestamp <= ?"
        params.append(parser.parse(end_str))
        
    query += " ORDER BY timestamp ASC"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    # Process for graphs
    # 1. Requests over time (bucketed by minute?)
    # 2. Status distribution
    
    data = [{
        'timestamp': row[0],
        'status': row[1],
        'duration': row[2],
        'service': row[3]
    } for row in rows]
    
    return jsonify(data)

@app.route('/api/logs')
def logs():
    limit = request.args.get('limit', 100)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM requests ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    init_db()
    t = threading.Thread(target=log_reader, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
