from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = "alignments.db"


# Inicializar DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS alignments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        muscle_content TEXT,
                        msa_content TEXT,
                        created_at TEXT
                    )''')
    conn.commit()
    conn.close()


init_db()


@app.route("/save", methods=["POST"])
def save_alignment():
    """Guarda un alineamiento en la base de datos"""
    data = request.get_json()
    filename = data.get("filename")
    muscle = data.get("muscle_content")
    msa = data.get("msa_content")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alignments (filename, muscle_content, msa_content, created_at) VALUES (?, ?, ?, ?)",
        (filename, muscle, msa, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})


@app.route("/list", methods=["GET"])
def list_alignments():
    """Devuelve historial resumido de alineamientos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, created_at FROM alignments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "filename": r[1], "created_at": r[2]}
        for r in rows
    ])


@app.route("/get/<int:aln_id>", methods=["GET"])
def get_alignment(aln_id):
    """Devuelve un alineamiento específico con todo su contenido"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, muscle_content, msa_content, created_at FROM alignments WHERE id=?", (aln_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "id": row[0],
            "filename": row[1],
            "muscle_content": row[2],
            "msa_content": row[3],
            "created_at": row[4]
        })
    else:
        return jsonify({"error": "Not found"}), 404

@app.route("/get/<int:alignment_id>", methods=["GET"])
def get_alignment_db(alignment_id):
    conn = sqlite3.connect("alignments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, data FROM alignments WHERE id=?", (alignment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "data": row[2]})
    else:
        return jsonify({"error": "Alineamiento no encontrado"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
