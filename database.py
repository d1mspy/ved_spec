# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('scores.db')
    with conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
    conn.close()

def submit_score(name: str, score: int):
    conn = sqlite3.connect('scores.db')
    with conn:
        c = conn.cursor()
        c.execute('INSERT INTO scores (name, score) VALUES (?, ?)', (name, score))
    conn.close()

def get_scores():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('SELECT name, score FROM scores ORDER BY score DESC LIMIT 10')
    scores = c.fetchall()
    conn.close()
    return scores
