#!/usr/bin/env python3
"""
Demo FM - Modulación en Frecuencia
==================================

Aplicación educativa interactiva para visualizar FM con mensajes no senoidales.

Ejecutar con:
    streamlit run src/main.py
"""
import sys
from pathlib import Path

# Añadir el directorio src/ al path para imports correctos
file_path = Path(__file__).resolve()
src_dir = file_path.parent
sys.path.insert(0, str(src_dir))

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from core import (
    generate_message,
    FMParameters,
    calculate_fm_signal,
    calculate_carrier,
    validate_nyquist,
    validate_samples_per_period,
)
from app.sidebar import render_sidebar
from app.components import render_metrics, render_about_section
from app.tabs import render_time_tab, render_spectrum_tab, render_demodulation_tab


# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Demo FM - Modulación en Frecuencia",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# ESTILOS PERSONALIZADOS
# ============================================================================
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    # Título principal
    st.markdown(
        '<h1 class="main-header">📡 Demo de Modulación FM</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Visualización interactiva de FM con mensajes no senoidales</p>',
        unsafe_allow_html=True,
    )

    # ============================================================================
    # SIDEBAR - CONTROLES
    # ============================================================================
    params_dict = render_sidebar()
    
    # Extraer parámetros
    waveform = params_dict["waveform"]
    Fs = params_dict["Fs"]
    dur = params_dict["dur"]
    fc = params_dict["fc"]
    fm = params_dict["fm"]
    Am = params_dict["Am"]
    kf = params_dict["kf"]
    H = params_dict["H"]
    show_carrier = params_dict["show_carrier"]

    # ============================================================================
    # CÓMPUTO DE SEÑALES
    # ============================================================================

    # Generar vector de tiempo
    N = int(Fs * dur)
    t = np.linspace(0, dur, N, endpoint=False)
    dt = 1.0 / Fs

    # Generar señal moduladora
    m = generate_message(t, fm, waveform, Am)
    m_norm = m / Am if Am > 0 else m  # Normalizada para demodulación

    # Calcular parámetros FM
    params = FMParameters(fc, fm, Am, kf, H)

    # Generar señales
    s, fi, _ = calculate_fm_signal(t, fc, kf, m, dt)
    c = calculate_carrier(t, fc) if show_carrier else None

    # ============================================================================
    # VALIDACIONES DE MUESTREO
    # ============================================================================

    # Validación 1: Nyquist
    nyquist_result = validate_nyquist(fc, params.delta_f, Fs)
    if not nyquist_result.is_valid:
        st.error(nyquist_result.message)
    elif nyquist_result.level == "warning":
        st.warning(nyquist_result.message)

    # Validación 2: Muestras por período
    samples_result = validate_samples_per_period(Fs, fm)
    if samples_result:
        st.info(samples_result.message)

    # ============================================================================
    # MÉTRICAS PRINCIPALES
    # ============================================================================

    render_metrics(params)
    st.divider()

    # ============================================================================
    # PESTAÑAS DE VISUALIZACIÓN
    # ============================================================================

    tabs = st.tabs(["⏱️ Tiempo", "📊 Espectro", "🔧 Demodulación"])

    # Tab 1: Tiempo
    with tabs[0]:
        render_time_tab(t, m, s, fi, c, params, show_carrier)

    # Tab 2: Espectro
    with tabs[1]:
        render_spectrum_tab(m, s, params, Fs, waveform)

    # Tab 3: Demodulación
    with tabs[2]:
        render_demodulation_tab(t, m_norm, s, params, Fs)

    # ============================================================================
    # INFORMACIÓN ADICIONAL
    # ============================================================================

    st.divider()
    render_about_section()


# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    main()
