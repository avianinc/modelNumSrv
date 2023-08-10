"""
---------------------------------------------------------------
Model Numbering Service - model_numbering_service.py
---------------------------------------------------------------

Description:
    A web service that manages model numbers. It supports 
    operations such as adding model types, pulling, 
    confirming, releasing, and searching numbers. The service 
    maintains its state in a SQLite database named `model_numbers.db`.

Author:
    John DeHart (jdehart@avian.com)

Date:
    Created on: August 10, 2023 

License:
    MIT License

"""

from datetime import datetime, timedelta
import sqlite3
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import configparser
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get("DEFAULT", "HOST", fallback="127.0.0.1")
PORT = int(config.get("DEFAULT", "PORT", fallback="5001"))
RELEASE_TIME = int(config.get("DEFAULT", "RELEASE_TIME", fallback="172800"))
CHECK_INTERVAL = int(config.get("DEFAULT", "CHECK_INTERVAL", fallback="3600"))

app = Flask(__name__)

DATABASE = "model_numbers.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_numbers (
            id INTEGER PRIMARY KEY,
            model_type TEXT NOT NULL UNIQUE,
            description TEXT,
            latest_number INTEGER NOT NULL DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_details (
            id INTEGER PRIMARY KEY,
            model_type TEXT NOT NULL,
            model_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pulled',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

@app.route('/add_model_type/<model_type>/<description>', methods=['POST'])
def add_model_type(model_type, description):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO model_numbers (model_type, description) VALUES (?, ?)", (model_type, description))
            conn.commit()
            return jsonify({"status": f"Model type {model_type} added with description: {description}"}), 200
        except sqlite3.IntegrityError:
            return jsonify({"error": "Model type already exists."}), 400

@app.route('/list_model_types', methods=['GET'])
def list_model_types():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_type, description FROM model_numbers")
        rows = cursor.fetchall()
        if rows:
            return jsonify({"model_types": [{ "type": row[0], "description": row[1] } for row in rows]}), 200
        else:
            return jsonify({"error": "No model types found."}), 404

@app.route('/pull/<model_type>', methods=['GET'])
def pull_number(model_type):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_number FROM model_details WHERE model_type=? AND status='released' ORDER BY model_number ASC LIMIT 1", (model_type,))
        row = cursor.fetchone()
        if row:
            model_number = row[0]
            cursor.execute("UPDATE model_details SET status='pulled', timestamp=? WHERE model_type=? AND model_number=?", (datetime.utcnow(), model_type, model_number))
            conn.commit()
            return jsonify({"number": model_number}), 200
        else:
            cursor.execute("SELECT latest_number FROM model_numbers WHERE model_type=?", (model_type,))
            row = cursor.fetchone()
            if row:
                latest_number = row[0] + 1
                cursor.execute("UPDATE model_numbers SET latest_number=? WHERE model_type=?", (latest_number, model_type))
                cursor.execute("INSERT INTO model_details (model_type, model_number, status) VALUES (?, ?, 'pulled')", (model_type, latest_number))
                conn.commit()
                return jsonify({"number": latest_number}), 200
            else:
                return jsonify({"error": "Model type not available. Please add a model type using add_model_type."}), 400

@app.route('/confirm/<model_type>/<number>', methods=['POST'])
def confirm(model_type, number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Check if the model number exists
        cursor.execute("SELECT status FROM model_details WHERE model_type=? AND model_number=?", (model_type, int(number)))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": f"Model {model_type}-{number} does not exist."}), 404  # 404 Not Found

        # If the model number exists, but has a different status
        if result[0] != 'pulled':
            if result[0] == 'confirmed':
                return jsonify({"error": f"Model {model_type}-{number} is already confirmed."}), 400  # 400 Bad Request
            else:
                return jsonify({"error": f"Model {model_type}-{number} cannot be confirmed in its current state."}), 400  # 400 Bad Request

        # Confirm the model number
        cursor.execute("UPDATE model_details SET status='confirmed' WHERE model_type=? AND model_number=? AND status='pulled'", (model_type, int(number)))
        conn.commit()

        if cursor.rowcount:
            return jsonify({"status": "confirmed"}), 200  # 200 OK
        else:
            return jsonify({"error": "Unexpected error while confirming."}), 500  # 500 Internal Server Error

@app.route('/release/<model_type>/<number>', methods=['POST'])
def release(model_type, number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Check if the model number exists
        cursor.execute("SELECT status FROM model_details WHERE model_type=? AND model_number=?", (model_type, int(number)))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": f"Model {model_type}-{number} does not exist."}), 404  # 404 Not Found

        # If the model number exists, but has a different status
        if result[0] != 'confirmed':
            if result[0] == 'released':
                return jsonify({"error": f"Model {model_type}-{number} is already released."}), 400  # 400 Bad Request
            else:
                return jsonify({"error": f"Model {model_type}-{number} cannot be released in its current state."}), 400  # 400 Bad Request

        # Release the model number
        cursor.execute("UPDATE model_details SET status='released' WHERE model_type=? AND model_number=? AND status='confirmed'", (model_type, int(number)))
        conn.commit()

        if cursor.rowcount:
            return jsonify({"status": "released"}), 200  # 200 OK
        else:
            return jsonify({"error": "Unexpected error while releasing."}), 500  # 500 Internal Server Error


@app.route('/search/<model_type>/<number>', methods=['GET'])
def search(model_type, number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM model_details WHERE model_type=? AND model_number=?", (model_type, int(number)))
        row = cursor.fetchone()

        # If a matching row was found
        if row:
            status = row[0]
            return jsonify({"status": status}), 200  # 200 OK
        else:
            # Return a more informative error message
            return jsonify({"error": f"Model number {model_type}-{number} not found in the database."}), 404  # 404 Not Found

def release_unconfirmed_numbers():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cutoff_time = datetime.utcnow() - timedelta(seconds=RELEASE_TIME)
        
        # Fetch numbers that are set to be released
        cursor.execute("SELECT * FROM model_details WHERE status='pulled'")
        all_pulled = cursor.fetchall()

        # Fetch numbers that should be released based on the timestamp
        cursor.execute("SELECT * FROM model_details WHERE status='pulled' AND timestamp < ?", (cutoff_time,))
        to_release = cursor.fetchall()

        # Update those entries' status to 'released'
        cursor.execute("UPDATE model_details SET status='released' WHERE status='pulled' AND timestamp < ?", (cutoff_time,))
        conn.commit()

        # Print the information to console for debugging
        # print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: Checking for numbers to release...")
        
        # if all_pulled:
        #     print(f"Currently pulled numbers:")
        #     for entry in all_pulled:
        #         print(f"Model type: {entry[1]}, Number: {entry[2]}, Timestamp: {entry[4]}")

        # if to_release:
        #     print(f"Releasing the following numbers:")
        #     for entry in to_release:
        #         print(f"Model type: {entry[1]}, Number: {entry[2]}, Timestamp: {entry[4]}")
        # else:
        #     print(f"No numbers found to release at this time.")

        # print("\n")  # Add a newline for clarity in the logs

if __name__ == '__main__':
    init_db()
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    # scheduler.add_job(release_unconfirmed_numbers, 'interval', hours=1)
    scheduler.add_job(release_unconfirmed_numbers, trigger='interval', seconds=CHECK_INTERVAL)
    scheduler.start()
    app.run(host=HOST, port=PORT)
