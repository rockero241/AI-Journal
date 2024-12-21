import os
from datetime import date
from openai import OpenAI
import tkinter as tk
from tkinter import ttk, messagebox

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
    def __init__(self, date, mood, gratitude, room_for_growth, thoughts):
        self.date = date
        self.mood = mood
        self.gratitude = gratitude
        self.room_for_growth = room_for_growth
        self.thoughts = thoughts

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


class JournalApp:
    """
    The main GUI for the journaling app using ttkinter.
    """
    def __init__(self, root):
        self.root = root
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
        ttk.Button(self.root, text="Submit", command=self.submit_entry).pack(pady=20)

    def submit_entry(self):
        """
        Process the journal entry, get feedback, and save it.
        """
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
        entry = Journal(self.date, mood, gratitude, room_for_growth, thoughts)

        # Get AI feedback if the user wants it
        feedback = None
        if self.feedback_var.get() == "yes":
            feedback = get_ai_feedback(entry)
            messagebox.showinfo("AI Feedback", feedback)

        # Save the entry to a file
        filename = save_entry_to_file(entry, feedback)
        messagebox.showinfo("Success", f"Journal entry saved as {filename}.")

        # Clear input fields
        self.clear_fields()

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
    """
    Main function to launch the journaling app.
    """
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

