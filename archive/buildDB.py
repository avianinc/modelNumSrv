import sqlite3

def setup_db():
    conn = sqlite3.connect('numbering.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS numbers (
        type TEXT PRIMARY KEY,
        latest_number INTEGER
    )
    ''')
    conn.commit()
    conn.close()

setup_db()
