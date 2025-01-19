import tkinter as tk
from tkinter import ttk, messagebox
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
            app = JournalApp(journal_window, username)
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
        ttk.Label(self.root, text=f"Welcome, {self.username}!", font=("Helvetica", 16)).pack(pady=20)
        ttk.Button(self.root, text="Create Entry", command=self.create_entry).pack(pady=10)
        ttk.Button(self.root, text="View Entry Log", command=self.view_entry_log).pack(pady=10)

    def create_entry(self):
        # Implement entry creation logic
        pass

    def view_entry_log(self):
        # Implement log viewing logic
        pass
