import sqlite3


class Journal:
    def __init__(self, date, mood, gratitude, room_for_growth, thoughts, username):
        self.date = date
        self.mood = mood
        self.gratitude = gratitude
        self.room_for_growth = room_for_growth
        self.thoughts = thoughts
        self.username = username

    def format_entry(self):
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
