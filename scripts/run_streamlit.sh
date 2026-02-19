#!/bin/bash
# Script para ejecutar la demo FM con Streamlit

echo "========================================"
echo "Demo FM - Modulación en Frecuencia"
echo "========================================"
echo ""
echo "Iniciando servidor Streamlit..."
echo "La aplicación se abrirá en tu navegador."
echo ""
echo "Presiona Ctrl+C para detener el servidor."
echo ""

cd "$(dirname "$0")/.." && ./venv/bin/streamlit run src/main.py
