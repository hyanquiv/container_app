from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

BACKEND_URL = "http://backend:5000"

@app.route("/")
def index():
    tareas = requests.get(f"{BACKEND_URL}/tareas").json()
    return render_template("index.html", tareas=tareas)

@app.route("/agregar", methods=["POST"])
def agregar():
    titulo = request.form["titulo"]
    requests.post(f"{BACKEND_URL}/tareas", json={"titulo": titulo})
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
