from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS barcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home page with form
@app.route('/')
def index():
    return render_template('index.html')

# Handle barcode submission
@app.route('/submit', methods=['POST'])
def submit():
    code = request.form['code']
    description = request.form['description']

    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()
    c.execute("INSERT INTO barcodes (code, description) VALUES (?, ?)", (code, description))
    conn.commit()
    conn.close()

    return redirect('/track')

# Display tracked barcodes
@app.route('/track')
def track():
    conn = sqlite3.connect('barcodes.db')
    c = conn.cursor()
    c.execute("SELECT * FROM barcodes ORDER BY timestamp DESC")
    barcodes = c.fetchall()
    conn.close()
    return render_template('track.html', barcodes=barcodes)

if __name__ == '__main__':
    app.run(debug=True)
