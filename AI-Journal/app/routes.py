import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from models import Journal
from core import hash_password, verify_password, get_ai_feedback, save_entry_to_file

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Journal Login")
        self.root.geometry("300x240")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

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
            JournalApp(journal_window, username)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def verify_credentials(self, username, password):
        import sqlite3

        conn = sqlite3.connect('journal.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash = result[0]
            return verify_password(password, stored_hash)
        return False

    def show_register(self):
        RegisterWindow(self.root)

class RegisterWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Create New Account")
        self.top.geometry("300x250")

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()

        ttk.Label(self.top, text="Create New Account", font=("Helvetica", 14)).pack(pady=10)
        ttk.Label(self.top, text="Username:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.username_var).pack()
        ttk.Label(self.top, text="Password:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.password_var, show="*").pack()
        ttk.Label(self.top, text="Confirm Password:").pack(pady=5)
        ttk.Entry(self.top, textvariable=self.confirm_password_var, show="*").pack()

        ttk.Button(self.top, text="Sign Up", command=self.create_account).pack(pady=20)

    def create_account(self):
        import sqlite3

        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            conn = sqlite3.connect('journal.db')
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Account created successfully!")
            self.top.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

class JournalApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Journaling App")
        self.root.geometry("400x500")
        self.create_main_menu()

    def create_main_menu(self):
        """
        Display the main menu with options to create an entry or view the entry log.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text=f"Welcome, {self.username}!", font=("Helvetica", 16)).pack(pady=20)
        ttk.Button(self.root, text="Create Entry", command=self.create_entry).pack(pady=10)
        ttk.Button(self.root, text="View Entry Log", command=self.view_entry_log).pack(pady=10)

    def create_entry(self):
        """
        Display the form to create a new journal entry.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Create Journal Entry", font=("Helvetica", 16)).pack(pady=10)

        # Input fields
        self.mood_var = tk.StringVar()
        self.gratitude_var = tk.StringVar()
        self.room_for_growth_var = tk.StringVar()
        self.thoughts_var = tk.StringVar()
        self.feedback_var = tk.StringVar(value="no")

        ttk.Label(self.root, text="Mood (e.g., great, good, meh, bad):").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.mood_var, width=40).pack(padx=10, pady=5)

        ttk.Label(self.root, text="What are you grateful for today?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.gratitude_var, width=40).pack(padx=10, pady=5)

        ttk.Label(self.root, text="What could have gone better today?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.room_for_growth_var, width=40).pack(padx=10, pady=5)

        ttk.Label(self.root, text="What's on your mind?").pack(anchor="w", padx=10)
        ttk.Entry(self.root, textvariable=self.thoughts_var, width=40).pack(padx=10, pady=5)

        ttk.Label(self.root, text="Do you want AI feedback?").pack(anchor="w", padx=10)
        feedback_frame = ttk.Frame(self.root)
        feedback_frame.pack(anchor="w", padx=10)
        ttk.Radiobutton(feedback_frame, text="Yes", variable=self.feedback_var, value="yes").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(feedback_frame, text="No", variable=self.feedback_var, value="no").pack(side=tk.LEFT, padx=5)

        ttk.Button(self.root, text="Submit Entry", command=self.submit_entry).pack(pady=20)
        ttk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=10)

    def submit_entry(self):
        """
        Save the journal entry to the database and provide feedback if requested.
        """
        from models import Journal
        from core import get_ai_feedback, save_entry_to_file

        mood = self.mood_var.get().strip()
        gratitude = self.gratitude_var.get().strip()
        room_for_growth = self.room_for_growth_var.get().strip()
        thoughts = self.thoughts_var.get().strip()

        if not all([mood, gratitude, room_for_growth, thoughts]):
            messagebox.showerror("Error", "Please fill out all fields.")
            return

        entry = Journal(
            date=date.today().strftime("%Y-%m-%d"),
            mood=mood,
            gratitude=gratitude,
            room_for_growth=room_for_growth,
            thoughts=thoughts,
            username=self.username,
        )

        feedback = None
        if self.feedback_var.get() == "yes":
            feedback = get_ai_feedback(entry)

        entry.save_to_db(feedback)
        save_entry_to_file(entry, feedback)

        messagebox.showinfo("Success", "Your journal entry has been saved!")
        self.create_main_menu()

    def view_entry_log(self):
        """
        Display all journal entries for the logged-in user.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Your Journal Entries", font=("Helvetica", 16)).pack(pady=10)

        # Text box to display entries
        self.entries_output = tk.Text(self.root, height=20, width=50, wrap=tk.WORD)
        self.entries_output.pack(padx=10, pady=10)

        # Fetch entries from the database
        import sqlite3

        conn = sqlite3.connect('journal.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT entry_date, mood, gratitude, room_for_growth, thoughts FROM entries WHERE username = ? ORDER BY entry_date DESC",
            (self.username,)
        )
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for row in rows:
                self.entries_output.insert(
                    tk.END,
                    f"Date: {row[0]}\nMood: {row[1]}\nGratitude: {row[2]}\nRoom for Growth: {row[3]}\nThoughts: {row[4]}\n{'-' * 40}\n",
                )
        else:
            self.entries_output.insert(tk.END, "No entries found.")

        ttk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=10)
