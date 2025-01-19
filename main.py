from core import init_db
import tkinter as tk
from gui import LoginWindow


def main():
    init_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
