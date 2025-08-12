#!/bin/bash
# Instalador automático del honeypot
set -e

echo "[+] Actualizando sistema..."
sudo apt update && sudo apt install -y python3 python3-pip

echo "[+] Instalando dependencias..."
pip3 install -r requirements.txt

echo "[+] Listo. Para ejecutar:"
echo "    python3 honeypot.py <URL_DEL_SITIO_A_CLONAR>"
echo "[+] Ejemplo:"
echo "    python3 honeypot.py https://example.com"

