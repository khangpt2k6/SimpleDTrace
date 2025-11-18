import requests
import time
import csv
import sqlite3
import os
from datetime import datetime
import statistics

DATABASE = 'database.db'
CSV_FILE = 'monitor_log.csv'
URL = 'http://localhost:5000/process'
DURATION = 300  # 5 minutes
INTERVAL = 0.3  # seconds between requests

def init_monitor_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitor_stats (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            success INTEGER NOT NULL,
            status_code INTEGER
        )
    ''')
    cursor.execute('DELETE FROM monitor_stats')
    conn.commit()
    conn.close()

def log_to_db(timestamp, latency_ms, success, status_code):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO monitor_stats (timestamp, latency_ms, success, status_code) VALUES (?, ?, ?, ?)',
                   (timestamp, latency_ms, success, status_code))
    conn.commit()
    conn.close()

def clear_monitoring_data():
    """Clear all monitoring-related data (CSV and database tables)"""
    # Clear CSV file (will be overwritten anyway, but explicit is better)
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        print(f"Cleared {CSV_FILE}")
    
    # Clear database tables
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Clear monitor_stats table
    cursor.execute('DELETE FROM monitor_stats')
    
    conn.commit()
    conn.close()
    print("Cleared monitoring data from database")

def main():
    # Clear old data before starting new monitoring session
    clear_monitoring_data()
    init_monitor_db()
    
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'latency_ms', 'success', 'status_code'])
        
        latencies = []
        successes = []
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < DURATION:
            request_start = time.time()
            try:
                response = requests.get(URL, timeout=10)
                latency = (time.time() - request_start) * 1000
                success = response.status_code == 200
                status_code = response.status_code
            except requests.RequestException:
                latency = (time.time() - request_start) * 1000
                success = False
                status_code = None
            
            timestamp = datetime.now().isoformat()
            
            writer.writerow([timestamp, latency, success, status_code])
            log_to_db(timestamp, latency, int(success), status_code)
            
            latencies.append(latency)
            successes.append(success)
            
            request_count += 1
            
            # Wait for next request
            elapsed = time.time() - request_start
            if elapsed < INTERVAL:
                time.sleep(INTERVAL - elapsed)
        
        # Summary
        total_requests = len(latencies)
        success_count = sum(successes)
        success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
        avg_latency = statistics.mean(latencies) if latencies else 0
        min_latency = min(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0
        
        print("Monitoring Summary:")
        print(f"Total requests: {total_requests}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Average latency: {avg_latency:.2f} ms")
        print(f"Min latency: {min_latency:.2f} ms")
        print(f"Max latency: {max_latency:.2f} ms")

if __name__ == '__main__':
    main()