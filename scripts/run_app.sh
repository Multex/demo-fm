#!/bin/bash

# Función para pausar en caso de error (similar a pause en Windows)
pause_on_error() {
    read -p "Presione Enter para salir..."
}

echo "Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no encontrado."
    echo "Por favor instale python3 (sudo apt install python3 o descargue de python.org)"
    pause_on_error
    exit 1
fi

echo "Instalando/Verificando librerías necesarias..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Hubo un problema instalando las librerías."
    echo "Verifique su conexión a internet."
    pause_on_error
    exit 1
fi

echo "Iniciando la aplicación..."
cd "$(dirname "$0")/.." && python3 -m streamlit run src/fm_demo_streamlit.py
