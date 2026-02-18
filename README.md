# Demo FM - Modulación en Frecuencia

Demo educativa simple de FM con mensajes no senoidales.

## 🚀 Cómo usar

### Opción 1: Streamlit (Recomendado - Interfaz moderna)

```bash
./run_streamlit.sh
```

Se abrirá en tu navegador automáticamente.

### Opción 2: Matplotlib (Interfaz básica con sliders)

```bash
python3 src/fm_non_sinusoidal_demo.py
```

## 📁 Archivos

- **src/fm_demo_streamlit.py** - Versión principal con Streamlit
- **run_streamlit.sh** - Script de ejecución (usando venv)
- **run_app.sh** / **run_app.bat** - Scripts de instalación y ejecución

## 🎛️ Controles

- Forma de onda: Cuadrada / Diente de Sierra / Triangular
- Fs, duración, fc, fm, Am, kf, H (armónicos)
- Checkbox para mostrar/ocultar portadora

## 📊 Visualiza

1. Señal moduladora m(t)
2. Señal FM s(t)
3. Señal portadora c(t) (opcional)
4. Frecuencia instantánea fi(t)

## 📐 KPIs mostrados

- Δf (kHz) - Desviación de frecuencia
- B (kHz) - Ancho de banda (Carson)
- fc (kHz) - Frecuencia portadora
- fm (Hz) - Frecuencia del mensaje
- β - Índice de modulación

---

**¡Eso es todo! .**
