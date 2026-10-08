from flask import Flask, render_template, jsonify
import Keero
import threading
import asyncio

def start_keero():
    asyncio.run(Keero.main())

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/status")
def status():
    data = {
        "recognized": Keero.recognized_text,
        "reply": Keero.robot_reply,
        "state": Keero.state
    }

    # 🔥 CRITICAL FIX (prevents repeat)
    Keero.recognized_text = ""
    Keero.robot_reply = ""

    return jsonify(data)

if __name__ == "__main__":
    print("Starting Keero brain...")
    threading.Thread(target=start_keero, daemon=True).start()

    print("Starting UI...")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)