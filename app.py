import sqlite3
import time
import random
from datetime import datetime
from flask import Flask, jsonify
import requests

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_calls (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            status_code INTEGER,
            latency_ms REAL
        )
    ''')
    # Pre-populate users if empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        users = []
        for i in range(1, 1001):
            users.append((i, f'User {i}', f'user{i}@example.com'))
        cursor.executemany('INSERT INTO users (id, name, email) VALUES (?, ?, ?)', users)
    conn.commit()
    conn.close()

def insert_log(message):
    conn = get_db()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('INSERT INTO logs (timestamp, message) VALUES (?, ?)', (timestamp, message))
    conn.commit()
    conn.close()

def insert_api_call(source, status_code, latency_ms):
    conn = get_db()
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('INSERT INTO api_calls (timestamp, source, status_code, latency_ms) VALUES (?, ?, ?, ?)', (timestamp, source, status_code, latency_ms))
    conn.commit()
    conn.close()

@app.route('/process', methods=['GET'])
def process():
    start_time = time.time()
    try:
        # Call external API with retry logic
        retries = 3
        timeout = 10
        for attempt in range(retries):
            try:
                response = requests.get('https://jsonplaceholder.typicode.com/posts/1', timeout=timeout)
                response.raise_for_status()
                post_data = response.json()
                user_id = post_data.get('userId')
                break
            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(1)  # Wait before retry

        # Chained request
        for attempt in range(retries):
            try:
                user_response = requests.get(f'https://jsonplaceholder.typicode.com/users/{user_id}', timeout=timeout)
                user_response.raise_for_status()
                user_data = user_response.json()
                break
            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(1)

        # Log API calls
        latency1 = (time.time() - start_time) * 1000
        insert_api_call('https://jsonplaceholder.typicode.com/posts/1', response.status_code, latency1)
        latency2 = (time.time() - start_time - latency1/1000) * 1000
        insert_api_call(f'https://jsonplaceholder.typicode.com/users/{user_id}', user_response.status_code, latency2)

        # Simulate heavy computation
        time.sleep(random.uniform(0.3, 0.5))

        total_latency = (time.time() - start_time) * 1000
        return jsonify({
            'status': 'success',
            'post': post_data,
            'user': user_data,
            'total_latency_ms': total_latency
        }), 200

    except requests.RequestException as e:
        insert_log(f'API call failed: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)