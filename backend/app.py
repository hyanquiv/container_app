from flask import Flask, request, jsonify
import os
from aligner import run_alignment
import uuid
import requests  # 👈 para comunicar con el contenedor db

app = Flask(__name__)

# Crear carpetas si no existen
os.makedirs("in", exist_ok=True)
os.makedirs("out", exist_ok=True)

DB_URL = "http://db:6000"  # 👈 usa el nombre del servicio en docker-compose


@app.route("/align", methods=["POST"])
def align():
    # Crear ruta única para input
    input_filename = f"{uuid.uuid4()}.fasta"
    input_path = os.path.join("in", input_filename)

    # Guardar input
    file = request.files["file"]
    file.save(input_path)

    # Ejecutar alineamiento → devuelve 2 paths
    muscle_path, msa_path = run_alignment(
        input_path, os.path.join("out", str(uuid.uuid4()))
    )

    # Leer alineamientos como texto plano
    with open(muscle_path, "r") as f1, open(msa_path, "r") as f2:
        muscle_text = f1.read()
        msa_text = f2.read()

    # Guardar en la base de datos
    try:
        requests.post(f"{DB_URL}/save", json={
            "filename": input_filename,
            "muscle_content": muscle_text,
            "msa_content": msa_text
        })
    except Exception as e:
        print(f"⚠️ No se pudo guardar en DB: {e}")

    # Borrar archivos temporales
    try:
        os.remove(input_path)
        os.remove(muscle_path)
        os.remove(msa_path)
    except Exception as e:
        print(f"Error al limpiar archivos: {e}")

    # Devolver ambos como JSON (texto plano)
    return jsonify({
        "aligned_muscle.fasta": muscle_text,
        "aligned_msa.fasta": msa_text
    })


@app.route("/alignments", methods=["GET"])
def get_alignments():
    """Devuelve el historial desde la DB"""
    try:
        resp = requests.get(f"{DB_URL}/list")
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con DB: {e}"}), 500

@app.route("/save", methods=["POST"])
def save_proxy():
    data = request.json
    try:
        resp = requests.post(f"{DB_URL}/save", json=data)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": f"No se pudo guardar en DB: {e}"}), 500

@app.route("/alignment/<int:alignment_id>", methods=["GET"])
def get_alignment(alignment_id):
    try:
        resp = requests.get(f"{DB_URL}/get/{alignment_id}")
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": f"No se pudo obtener el alineamiento: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
