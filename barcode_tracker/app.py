from flask import Flask, render_template, request, redirect
import sqlite3, os, datetime
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
BARCODE_FOLDER = 'static/barcodes'
os.makedirs(BARCODE_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            description TEXT,
            customer_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            inward_time TEXT,
            calibration_time TEXT,
            qc_time TEXT,
            documentation_time TEXT,
            billing_time TEXT,
            dispatch_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_barcode(code):
    filepath = os.path.join(BARCODE_FOLDER, f"{code}.png")
    if not os.path.exists(filepath):
        img = Image.new('RGB', (400, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 40)
        else:
            font = ImageFont.load_default()
        draw.text((10, 25), code, font=font, fill=(0, 0, 0))
        img.save(filepath)
    return filepath

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    description = request.form['description']
    customer = request.form['customer']
    code = f"INST{int(datetime.datetime.now().timestamp())}"
    barcode_path = generate_barcode(code)
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute("INSERT INTO instruments (code, description, customer_name, inward_time) VALUES (?, ?, ?, ?)",
              (code, description, customer, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return render_template('print.html', code=code, barcode_img=barcode_path)

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        code = request.form['code']
        stage = request.form['stage']
        now = datetime.datetime.now().isoformat()
        if stage in ["inward", "calibration", "qc", "documentation", "billing", "dispatch"]:
            conn = sqlite3.connect('tracker.db')
            c = conn.cursor()
            c.execute(f"UPDATE instruments SET {stage}_time = ? WHERE code = ?", (now, code))
            conn.commit()
            conn.close()
        return redirect('/track')
    return render_template('scan.html')

@app.route('/track')
def track():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute("SELECT * FROM instruments ORDER BY created_at DESC")
    data = c.fetchall()
    conn.close()
    return render_template('track.html', instruments=data)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
