import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import time
from flask import Flask, jsonify
import threading

# Database setup
def setup_database():
    """Create the database and table if they do not exist."""
    conn = sqlite3.connect('otp_history.db')  # Creates a file-based database
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            otp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_otp_to_db(timestamp, otp):
    """Insert a new OTP record into the database."""
    conn = sqlite3.connect('otp_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO otp_history (timestamp, otp) VALUES (?, ?)', (timestamp, otp))
    conn.commit()
    conn.close()

def fetch_and_save_otp():
    """Fetch OTP from website and save to database."""
    url = "https://otp-generator-sm20.onrender.com/"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            otp_div = soup.find('div', class_='otp')
            
            if otp_div:
                otp = otp_div.text.strip()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to database
                save_otp_to_db(current_time, otp)
                
                print(f"Time: {current_time}")
                print(f"OTP: {otp}")
                print("Saved to database.")
                print("-" * 30)
            else:
                print("Could not find OTP on page")
        else:
            print(f"Error: Status code {response.status_code}")
    except Exception as e:
        print(f"Error occurred: {e}")

def start_otp_fetcher():
    """Run the OTP fetching loop."""
    print("Starting OTP Fetcher...")
    print("Fetching OTP every 30 seconds. Press Ctrl+C to stop.")
    
    # Setup the database before starting
    setup_database()
    
    while True:
        try:
            fetch_and_save_otp()
            time.sleep(30)  # Wait 30 seconds before fetching the next OTP
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Retry after 5 seconds if an error occurs

# Flask app setup
app = Flask(__name__)

DB_PATH = 'otp_history.db'  # Path to your SQLite database

def fetch_latest_otp():
    """Fetch the latest OTP from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM otp_history ORDER BY id DESC LIMIT 1')  # Get the latest OTP
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

@app.route('/otp', methods=['GET'])
def get_latest_otp():
    """API endpoint to return the latest OTP."""
    otp_record = fetch_latest_otp()
    if otp_record:
        return jsonify(otp_record)  # Return OTP as JSON
    else:
        return jsonify({'error': 'No OTP available'}), 404

if __name__ == "__main__":
    # Run the OTP fetcher in a separate thread
    fetcher_thread = threading.Thread(target=start_otp_fetcher, daemon=True)
    fetcher_thread.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=8000)
