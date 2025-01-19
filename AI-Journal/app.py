from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Your Flask Journal!"

@app.route('/create', methods=['GET', 'POST'])
def create_entry():
    if request.method == 'POST':
        mood = request.form['mood']
        gratitude = request.form['gratitude']
        room_for_growth = request.form['room_for_growth']
        thoughts = request.form['thoughts']
        # For now, print to console; later, we save to a database
        print(f"New Entry: Mood: {mood}, Gratitude: {gratitude}, Growth: {room_for_growth}, Thoughts: {thoughts}")
        return "Entry Submitted Successfully!"
    return '''
    <form method="post">
        Mood: <input type="text" name="mood"><br>
        Gratitude: <input type="text" name="gratitude"><br>
        Room for Growth: <input type="text" name="room_for_growth"><br>
        Thoughts: <textarea name="thoughts"></textarea><br>
        <input type="submit">
    </form>
    '''

@app.route('/view')
def view_entries():
    # This will later fetch entries from the database
    return "Viewing All Entries (Coming Soon)"

if __name__ == "__main__":
    app.run(debug=True)
