# quesofr33
Honeypot que clona una web y la pone con algunos puertos disponibles para ser hackeada pero registrando actividad.

Este proyecto es un honeypot web local capaz de clonar cualquier sitio web y usarlo como trampa para capturar y analizar interacciones maliciosas.
Puede simular formularios vulnerables y almacenar en un log toda la actividad recibida.

🚀 Características
Clona cualquier sitio web estático (HTML, CSS, JS) para servirlo localmente.

Intercepta peticiones y captura:

Campos de formularios (POST y GET).

Headers HTTP enviados por el cliente.

Cualquier intento de comando malicioso (inyección SQL, XSS, etc.).

Muestra actividad en la terminal en tiempo real.

Guarda registros en un archivo honeypot_log.txt para análisis posterior.

Fácil de instalar y ejecutar en cualquier Linux con Python 3.

Código limpio y listo para modificar.

📦 Requerimientos
Python 3.8+

Librerías Python:

Flask

requests

beautifulsoup4

📥 Instalación
Método 1: Manual

sudo apt update && sudo apt install python3 python3-pip -y
pip3 install flask requests beautifulsoup4
Método 2: Script automático

Ejecuta el script install.sh incluido:
chmod +x install.sh
./install.sh

⚙ Uso
Clona este repositorio o descarga los archivos.

Ejecuta el honeypot especificando la URL a clonar:
python3 queso.py --url "https://ejemplo.com" --port 8080

Abre en el navegador:
http://localhost:8080

Cualquier interacción se registrará en:
honeypot_log.txt

📂 Archivos
honeypot.py → Script principal.

install.sh → Script de instalación automática de dependencias.

requirements.txt → Lista de dependencias.

honeypot_log.txt → Registro de interacciones capturadas.

⚠ Advertencia Legal
Este proyecto es únicamente para propósitos educativos y de investigación en entornos controlados.
No debe usarse para interceptar información sin consentimiento. El autor no se hace responsable del mal uso.

🧠 Ejemplo de ejecución


python3 honeypot.py --url "https://victimasimulada.com" --port 5000
📜 Salida en terminal:

[INFO] Clonando https://victimasimulada.com...
[INFO] Honeypot activo en http://0.0.0.0:5000
[LOG] [IP: 192.168.1.23] POST -> {'usuario': 'admin', 'password': "' OR 1=1 --"}
