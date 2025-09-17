from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
DB_URL = "http://db:6000"

@app.get("/tareas")
def get_tareas():
    return requests.get(f"{DB_URL}/tareas").json()

@app.post("/tareas")
def add_tarea():
    data = request.get_json()
    requests.post(f"{DB_URL}/tareas", json=data)
    return {"msg": "Tarea agregada"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
