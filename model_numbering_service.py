from flask import Flask, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE = "model_numbers.db"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_numbers (
            id INTEGER PRIMARY KEY,
            model_type TEXT NOT NULL UNIQUE,
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

@app.route('/add_model_type/<model_type>', methods=['POST'])
def add_model_type(model_type):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO model_numbers (model_type) VALUES (?)", (model_type,))
            conn.commit()
            return jsonify({"status": "Model type added successfully!"}), 200
        except sqlite3.IntegrityError:
            return jsonify({"error": "Model type already exists!"}), 400

@app.route('/list_model_types', methods=['GET'])
def list_model_types():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_type FROM model_numbers")
        model_types = [row[0] for row in cursor.fetchall()]
        return jsonify({"model_types": model_types}), 200

@app.route('/pull/<model_type>', methods=['GET'])
def pull_number(model_type):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_number FROM model_details WHERE model_type=? AND status='released' ORDER BY model_number ASC LIMIT 1", (model_type,))
        row = cursor.fetchone()
        if row:
            model_number = row[0]
            cursor.execute("UPDATE model_details SET status='pulled', timestamp=CURRENT_TIMESTAMP WHERE model_type=? AND model_number=?", (model_type, model_number))
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
        cursor.execute("UPDATE model_details SET status='confirmed' WHERE model_type=? AND model_number=? AND status='pulled'", (model_type, int(number)))
        conn.commit()
        if cursor.rowcount:
            return jsonify({"status": "confirmed"}), 200
        else:
            return jsonify({"error": "Invalid operation."}), 400

@app.route('/release/<model_type>/<number>', methods=['POST'])
def release(model_type, number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE model_details SET status='released' WHERE model_type=? AND model_number=? AND status='confirmed'", (model_type, int(number)))
        conn.commit()
        if cursor.rowcount:
            return jsonify({"status": "released"}), 200
        else:
            return jsonify({"error": "Invalid operation."}), 400

@app.route('/search/<model_type>/<number>', methods=['GET'])
def search(model_type, number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM model_details WHERE model_type=? AND model_number=?", (model_type, int(number)))
        row = cursor.fetchone()
        if row:
            status = row[0]
            return jsonify({"status": status}), 200
        else:
            return jsonify({"error": "Number not found."}), 404

def release_unconfirmed_numbers():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cutoff_time = datetime.now() - timedelta(hours=48)
        cursor.execute("UPDATE model_details SET status='released' WHERE status='pulled' AND timestamp < ?", (cutoff_time,))
        conn.commit()

if __name__ == '__main__':
    init_db()
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(release_unconfirmed_numbers, 'interval', hours=1)
    scheduler.start()
    app.run(port=5001)
