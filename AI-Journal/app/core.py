import sqlite3
import os
import hashlib
import hmac
import base64
from datetime import date
from openai import OpenAI

# Load the API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set 'OPENAI_API_KEY' as an environment variable.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def init_db():
    conn = sqlite3.connect('journal.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            entry_date TEXT NOT NULL,
            mood TEXT NOT NULL,
            gratitude TEXT NOT NULL,
            room_for_growth TEXT NOT NULL,
            thoughts TEXT NOT NULL,
            ai_feedback TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')

    conn.commit()
    conn.close()


def hash_password(password):
    salt = os.urandom(16)
    iterations = 100000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)
    storage = salt + key
    return base64.b64encode(storage).decode('utf-8')


def verify_password(password, stored_hash):
    try:
        decoded = base64.b64decode(stored_hash.encode('utf-8'))
        salt = decoded[:16]
        key = decoded[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=32)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


def get_ai_feedback(entry):
    messages = [
        {"role": "system", "content": "You are a wise life coach providing constructive feedback based on a journal entry."},
        {"role": "user", "content": entry.format_entry()}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content.strip()


def save_entry_to_file(entry, feedback):
    filename = f"journal_{date.today().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w") as file:
        file.write(entry.format_entry())
        if feedback:
            file.write("\nAI Feedback:\n")
            file.write(feedback)
    return filename
