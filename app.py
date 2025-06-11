from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Hello from Barcode Tracker!"

if __name__ == "__main__":
    # Make it publicly accessible on Render
    app.run(host="0.0.0.0", port=10000)
