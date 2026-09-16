"""
api.py - Entry point server kompatibel dengan struktur proyek @devilda_id
Menjalankan FruitFresh AI Flask web server pada port 5000.
"""

from web_app import app

if __name__ == "__main__":
    print("[FruitFresh AI] Starting Flask server on http://127.0.0.1:5005")
    app.run(host="0.0.0.0", port=5005, debug=False)
