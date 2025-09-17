from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "tareas.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY, titulo TEXT)")
    conn.commit()
    conn.close()

@app.get("/tareas")
def get_tareas():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, titulo FROM tareas")
    rows = [{"id": r[0], "titulo": r[1]} for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.post("/tareas")
def add_tarea():
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO tareas (titulo) VALUES (?)", (data["titulo"],))
    conn.commit()
    conn.close()
    return {"msg": "Tarea insertada"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=6000)
