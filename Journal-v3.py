import os
from datetime import date
from openai import OpenAI
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Load the API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Set 'OPENAI_API_KEY' as an environment variable.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


class Journal:
    """
    A simple class to hold journal entry data.
    """
    def __init__(self, date, mood, gratitude, room_for_growth, thoughts, username):
        self.date = date
        self.mood = mood
        self.gratitude = gratitude
        self.room_for_growth = room_for_growth
        self.thoughts = thoughts
        self.username = username

    def format_entry(self):
        """
        Format the journal entry for saving.
        """
        return (
            f"Date: {self.date}\n"
            f"Mood: {self.mood}\n\n"
            f"What went well:\n{self.gratitude}\n\n"
            f"What could have gone better:\n{self.room_for_growth}\n\n"
            f"Thoughts:\n{self.thoughts}\n"
            f"{'-' * 40}\n"
        )
    
    def save_to_db(self, ai_feedback=None):
        conn = sqlite3.connect('journal.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO entries (username, entry_date, mood, gratitude, room_for_growth, thoughts, ai_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.username, self.date, self.mood, self.gratitude, self.room_for_growth, self.thoughts, ai_feedback))
        conn.commit()
        conn.close()


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
    
    # Modify entries table to include user_id
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

def get_ai_feedback(entry):
    """
    Get AI feedback for a journal entry using OpenAI.
    """
    messages = [
        {"role": "system", "content": "You are a wise life coach who provides feedback based on a user's journaling entry, and gives simple, straightforward and practical advice. Make sure to be relevant to what the user journaled today"},
        {"role": "user", "content": (
            f"Here's my journal entry:\n\n"
            f"Date: {entry.date}\n"
            f"Mood: {entry.mood}\n"
            f"What went well:\n{entry.gratitude}\n"
            f"What could have gone better:\n{entry.room_for_growth}\n"
            f"Thoughts:\n{entry.thoughts}\n\n"
            f"Please provide positive, constructive feedback."
        )}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content.strip()


def save_entry_to_file(entry, feedback):
    """
    Save the journal entry and AI feedback to a file.
    """
    filename = f"journal_{date.today().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w") as file:
        file.write(entry.format_entry())
        if feedback:
            file.write("\nAI Feedback:\n")
            file.write(feedback)
    return filename


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Journal Login")
        self.root.geometry("300x240")

        # Variables for user inputs
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Create widgets
        ttk.Label(root, text="Login to Your Journal", font=("Helvetica", 14)).pack(pady=10)

        ttk.Label(root, text="Username:").pack(pady=5)
        ttk.Entry(root, textvariable=self.username_var).pack()

        ttk.Label(root, text="Password:").pack(pady=5)
        ttk.Entry(root, textvariable=self.password_var, show="*").pack()

        ttk.Button(root, text="Login", command=self.login).pack(pady=10)
        ttk.Button(root, text="Register", command=self.show_register).pack()

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if self.verify_credentials(username, password):
            self.root.withdraw()
            journal_window = tk.Toplevel()
            app = JournalApp(journal_window, username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_register(self):
        SignUpWindow(self.root)

    def verify_credentials(self, username, password):
        conn = sqlite3.connect('journal.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash = result[0]
            return verify_password(password, stored_hash)
        return False
import hashlib
import hmac
import base64

def hash_password(password):
    """Hash a password using PBKDF2."""
    salt = os.urandom(16)  # Generate a random salt
    iterations = 100000    # Number of iterations

    # Generate the hash using PBKDF2
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations,
        dklen=32  # Length of the derived key
    )

    # Combine salt and key for storage
    storage = salt + key
    return base64.b64encode(storage).decode('utf-8')

def verify_password(password, stored_hash):
    """Verify a password against its stored hash."""
    try:
        # Decode the stored hash
        decoded = base64.b64decode(stored_hash.encode('utf-8'))
        salt = decoded[:16]  # First 16 bytes are salt
        key = decoded[16:]   # Rest is the key

        # Generate hash of provided password
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=32
        )

        # Compare in constant time to prevent timing attacks
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


class SignUpWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Create New Account")
        self.top.geometry("300x250")

        # Variables for user inputs
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        # Create widgets
        ttk.Label(self.top, text="Create New Account", font=("Helvetica", 14)).pack(pady=10)

        ttk.Label(self.top, text="Username:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.username_var).pack()

        ttk.Label(self.top, text="Password:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.password_var, show="*").pack()

        ttk.Label(self.top, text="Confirm Password:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.confirm_password_var, show="*").pack()

        ttk.Button(self.top, text="Sign Up", command=self.create_account).pack(pady=20)

    def create_account(self):
        username = self.username_var.get()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if self.create_user(username, password):
            messagebox.showinfo("Success", "Account created successfully!")
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Username already exists")

    def create_user(self, username, password):
        try:
            conn = sqlite3.connect('journal.db')
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False


class JournalApp:
    """
    The main GUI for the journaling app using ttkinter.
    """
    def __init__(self, root, username):
        self.root = root
        self.username = username
        #self.user_id = self.get_user_id()
        self.root.title("Journaling App")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Variables for user inputs
        self.date = date.today().strftime("%Y-%m-%d")
        self.mood_var = tk.StringVar()
        self.gratitude_var = tk.StringVar()
        self.room_for_growth_var = tk.StringVar()
        self.thoughts_var = tk.StringVar()
        self.feedback_var = tk.StringVar(value="no")

        # Build the GUI
        self.create_widgets()

    def get_user_id(self):
        """Retrieve user ID from database based on username"""
        conn = sqlite3.connect('journal.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = ?', (self.username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def create_widgets(self):
        """
           Create and layout widgets using ttk.
           """
        # Title
        ttk.Label(self.root, text="Journaling App", font=("Helvetica", 16)).pack(pady=10)

        # Mood input
        ttk.Label(self.root, text="Mood (e.g., great, good, meh, bad):").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.mood_var, width=40).pack(padx=10, pady=5)

        # Gratitude input
        ttk.Label(self.root, text="What are you grateful for today?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.gratitude_var, width=40).pack(padx=10, pady=5)

        # Room for growth input
        ttk.Label(self.root, text="What could have gone better today?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.room_for_growth_var, width=40).pack(padx=10, pady=5)

        # Thoughts input
        ttk.Label(self.root, text="What's on your mind?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.thoughts_var, width=40).pack(padx=10, pady=5)

        # AI Feedback option
        ttk.Label(self.root, text="Do you want AI feedback?").pack(anchor="w", padx=10)
        feedback_frame = ttk.Frame(self.root)
        feedback_frame.pack(anchor="w", padx=10)
        ttk.Radiobutton(feedback_frame, text="Yes", variable=self.feedback_var, value="yes").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(feedback_frame, text="No", variable=self.feedback_var, value="no").pack(side=tk.LEFT, padx=5)

        # Submit button
        ttk.Button(self.root, text="Submit Entry", command=self.submit_entry).pack(pady=10)

        # Divider
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", pady=10)

        # View Entries by Date
        ttk.Label(self.root, text="View Entries by Date (YYYY-MM-DD):").pack(anchor="w", padx=10)
        self.date_var = tk.StringVar()  # For user input
        ttk.Entry(self.root, textvariable=self.date_var, width=20).pack(padx=10, pady=5)
        ttk.Button(self.root, text="View", command=self.view_entries_by_date).pack(pady=5)
        self.entries_output = tk.Text(self.root, height=10, width=50)  # To display entries
        self.entries_output.pack(padx=10, pady=5)

    def submit_entry(self):
        # Get inputs from the user
        mood = self.mood_var.get().strip()
        gratitude = self.gratitude_var.get().strip()
        room_for_growth = self.room_for_growth_var.get().strip()
        thoughts = self.thoughts_var.get().strip()

        # Check if all fields are filled
        if not all([mood, gratitude, room_for_growth, thoughts]):
            messagebox.showerror("Error", "Please fill out all fields.")
            return

        # Create the journal entry
        entry = Journal(self.date, mood, gratitude, room_for_growth, thoughts, self.username)

        # Get AI feedback if selected
        feedback = None
        if self.feedback_var.get() == "yes":
            feedback = get_ai_feedback(entry)

        # Save to database
        entry.save_to_db(feedback)

        # Save the entry to a file
        filename = save_entry_to_file(entry, feedback)
        messagebox.showinfo("Success", f"Journal entry saved as {filename}.")

        # Clear input fields
        self.clear_fields()


    def view_entries_by_date(self):
        """
        Display journal entries for a specific date.
        """
        selected_date = self.date_var.get().strip()
        if not selected_date:
            messagebox.showerror("Error", "Please enter a valid date.")
            return

        try:
            conn = sqlite3.connect('journal.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT entry_date, mood, gratitude, room_for_growth, thoughts FROM entries WHERE entry_date = ? AND username = ?",
                (selected_date, self.username))
            rows = cursor.fetchall()
            conn.close()

            # Display entries in the text box
            self.entries_output.delete(1.0, tk.END)
            if rows:
                for row in rows:
                    self.entries_output.insert(tk.END,
                                               f"Date: {row[0]}\nMood: {row[1]}\nGratitude: {row[2]}\nRoom for Growth: {row[3]}\nThoughts: {row[4]}\n{'-' * 40}\n")
            else:
                self.entries_output.insert(tk.END, "No entries found for this date.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    def clear_fields(self):
        """
        Clear all input fields after submission.
        """
        self.mood_var.set("")
        self.gratitude_var.set("")
        self.room_for_growth_var.set("")
        self.thoughts_var.set("")
        self.feedback_var.set("no")


def main():
    init_db()
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

