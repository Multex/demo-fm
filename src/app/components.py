"""
Componentes reutilizables de la UI.
"""
import streamlit as st
import numpy as np
from core.fm_calculator import FMParameters


def render_metrics(params: FMParameters):
    """
    Renderiza las métricas principales en columnas.
    
    Args:
        params: Objeto FMParameters con los valores calculados
    """
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

    with col_m1:
        st.metric(
            label="🎯 Desviación de frecuencia",
            value=f"{params.delta_f_khz:.2f} kHz",
            help="Δf = kf · max|m(t)|",
        )

    with col_m2:
        st.metric(
            label="📏 Ancho de banda (Carson)",
            value=f"{params.B_carson_khz:.2f} kHz",
            help="Para mensajes no senoidales usamos f_{m,max} = H·fm. H representa la cantidad aproximada de armónicos significativos de la señal moduladora.",
        )

    with col_m3:
        st.metric(
            label="📡 Frecuencia portadora",
            value=f"{params.fc_mhz:.2f} MHz",
            help="Frecuencia central de la señal FM",
        )

    with col_m4:
        st.metric(
            label="🎵 Frecuencia del mensaje",
            value=f"{params.fm_khz:.2f} kHz",
            help="Frecuencia de la señal moduladora",
        )

    with col_m5:
        beta_display = f"{params.beta:.2f}" if params.beta != np.inf else "∞"
        st.metric(
            label="📊 Índice de modulación β",
            value=beta_display,
            help="β = Δf / fm",
        )


def render_snr_quality_indicator(snr_db: int):
    """
    Renderiza un indicador visual de calidad basado en SNR.
    
    Args:
        snr_db: Valor de SNR en dB
    """
    if snr_db >= 25:
        st.success("✅ Excelente")
    elif snr_db >= 15:
        st.warning("⚠️ Buena")
    elif snr_db >= 10:
        st.warning("⚠️ Regular")
    else:
        st.error("❌ Mala")


def render_about_section():
    """Renderiza la sección 'Acerca de' en un expander."""
    with st.expander("ℹ️ Acerca de esta demo"):
        st.markdown("""
        ### 📚 Modulación en Frecuencia (FM)

        Esta demo interactiva permite explorar cómo funciona la **modulación en frecuencia**
        cuando la señal moduladora no es senoidal (ondas cuadradas, diente de sierra o triangulares).

        **Conceptos clave:**
        - **Señal portadora c(t):** Señal coseno de alta frecuencia que se modula
        - **Señal moduladora m(t):** Contiene la información que queremos transmitir
        - **Frecuencia portadora fc:** Frecuencia base de la portadora
        - **Sensibilidad kf:** Controla cuánto varía la frecuencia por cada voltio de m(t)
        - **Señal FM s(t):** Resultado de modular la portadora con el mensaje
        - **Frecuencia instantánea fi(t):** La frecuencia de la portadora varía según m(t)
        - **Regla de Carson:** Estima el ancho de banda necesario considerando armónicos

        **Instrucciones:**
        1. Use los controles del panel izquierdo para ajustar parámetros
        2. Observe cómo cambian las señales en tiempo real
        3. Experimente con diferentes formas de onda y valores de kf
        4. Active/desactive el checkbox para comparar con la portadora
        5. Note cómo H (armónicos) afecta el ancho de banda de Carson

        ---

        **Desarrollado con:** Python, NumPy, Matplotlib, Streamlit
        **Propósito:** Educativo
        """)
