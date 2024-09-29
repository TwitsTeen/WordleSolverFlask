from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Function to initialize the database with 5-letter words
def init_db():
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS words (word TEXT)')
    with open('words.txt', 'r') as file:
        words = file.readlines()
        for word in words:
            word = word.strip().lower()
            c.execute('INSERT OR IGNORE INTO words (word) VALUES (?)', (word,))
    conn.commit()
    # Only keep words that are exactly 5 letters long
    c.execute('DELETE FROM words WHERE LENGTH(word) != 5')
    conn.commit()
    conn.close()

# Function to reset the temp table
def reset_temp():
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS temp')
    c.execute('CREATE TABLE temp AS SELECT * FROM words')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    notInTheWord = request.form.get('notInTheWord', '')
    inTheWord = request.form.get('inTheWord', '')
    correctlyPlaced = request.form.get('correctlyPlaced', '')

    reset_temp()

    conn = sqlite3.connect('words.db')
    c = conn.cursor()

    # Remove words containing any letters in notInTheWord
    for letter in notInTheWord:
        c.execute('DELETE FROM temp WHERE word LIKE ?', ('%' + letter + '%',))

    # Remove words that do not contain letters in inTheWord at any position
    for letter in inTheWord:
        c.execute('DELETE FROM temp WHERE word NOT LIKE ?', ('%' + letter + '%',))

    
    # Remove words where letters in correctlyPlaced are not in the correct positions
    for index, letter in enumerate(correctlyPlaced):
        if letter != '_':  # Check if the letter is not an underscore (meaning it needs to be in a fixed position)
            position = index + 1  # SQL positions are 1-indexed, so we adjust for that
            c.execute(f'DELETE FROM temp WHERE SUBSTR(word, ?, 1) != ?', (position, letter))

    c.execute('SELECT * FROM temp')
    words = c.fetchall()
    conn.close()

    return render_template('index.html', words=words)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
