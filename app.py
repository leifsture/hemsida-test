from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder=".")
CORS(app)
DB = "personer.db"

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS personer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fornamn TEXT NOT NULL,
                efternamn TEXT NOT NULL,
                postnummer TEXT NOT NULL,
                ort TEXT NOT NULL,
                skapad TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

# Servera index.html på startsidan
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Servera lista.html
@app.route("/lista")
def lista_sida():
    return send_from_directory(".", "lista.html")

# Spara en ny person
@app.route("/spara", methods=["POST"])
def spara():
    data = request.json
    fornamn = data.get("fornamn", "").strip()
    efternamn = data.get("efternamn", "").strip()
    postnummer = data.get("postnummer", "").strip()
    ort = data.get("ort", "").strip()

    if not all([fornamn, efternamn, postnummer, ort]):
        return jsonify({"status": "fel", "meddelande": "Alla fält måste fyllas i"}), 400

    with get_db() as con:
        con.execute(
            "INSERT INTO personer (fornamn, efternamn, postnummer, ort) VALUES (?,?,?,?)",
            (fornamn, efternamn, postnummer, ort)
        )
    return jsonify({"status": "ok", "meddelande": f"Sparat! {fornamn} {efternamn} har lagts till."})

# Hämta alla personer
@app.route("/api/personer", methods=["GET"])
def hamta_personer():
    with get_db() as con:
        rows = con.execute("SELECT * FROM personer ORDER BY skapad DESC").fetchall()
    return jsonify([dict(r) for r in rows])

# Ta bort en person
@app.route("/api/personer/<int:person_id>", methods=["DELETE"])
def ta_bort(person_id):
    with get_db() as con:
        con.execute("DELETE FROM personer WHERE id = ?", (person_id,))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    init_db()
    print("\n✅ Servern startar!")
    print("📋 Formulär:  http://localhost:5000")
    print("📊 Se data:   http://localhost:5000/lista\n")
    app.run(debug=True, port=5000)
