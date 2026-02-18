#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

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
# GENERADORES DE ONDAS (sin cache - se recalculan rápido)
# ============================================================================


def square_wave(t, fm):
    """Genera una onda cuadrada normalizada a ±1."""
    return np.sign(np.sin(2 * np.pi * fm * t))


def sawtooth_wave(t, fm):
    """Genera una onda diente de sierra normalizada a ±1."""
    T = 1.0 / fm
    return 2 * ((t / T) - np.floor(0.5 + t / T))


def triangle_wave(t, fm):
    """Genera una onda triangular normalizada a ±1."""
    T = 1.0 / fm
    return 2 * np.abs(2 * ((t / T) - np.floor(0.5 + t / T))) - 1


def sine_wave(t, fm):
    """Genera una onda senoidal normalizada a ±1."""
    return np.sin(2 * np.pi * fm * t)


# ============================================================================
# FUNCIONES UTILITARIAS PARA ANÁLISIS
# ============================================================================


def compute_spectrum(signal, Fs, max_freq=None):
    """
    Calcula el espectro de frecuencias (FFT) de una señal.

    Returns:
        freqs: Vector de frecuencias (Hz)
        magnitude: Magnitud del espectro (escala lineal)
        magnitude_db: Magnitud en dB
    """
    N = len(signal)
    # FFT y frecuencias
    fft_vals = np.fft.fft(signal)
    fft_freq = np.fft.fftfreq(N, 1/Fs)

    # Solo frecuencias positivas
    pos_mask = fft_freq >= 0
    freqs = fft_freq[pos_mask]
    magnitude = np.abs(fft_vals[pos_mask]) / N  # Normalizar

    # Convertir a dB (evitar log(0))
    magnitude_db = 20 * np.log10(magnitude + 1e-12)

    # Limitar a max_freq si se especifica
    if max_freq is not None:
        freq_mask = freqs <= max_freq
        freqs = freqs[freq_mask]
        magnitude = magnitude[freq_mask]
        magnitude_db = magnitude_db[freq_mask]

    return freqs, magnitude, magnitude_db


def demodulate_fm(s_fm, fc, Fs):
    """
    Demodula una señal FM usando diferenciación de fase.

    Args:
        s_fm: Señal FM
        fc: Frecuencia portadora (Hz)
        Fs: Frecuencia de muestreo (Hz)

    Returns:
        m_recovered: Señal mensaje recuperada (normalizada)
    """
    # Calcular la fase instantánea usando la transformada de Hilbert
    analytic_signal = s_fm + 1j * np.imag(np.fft.ifft(np.fft.fft(s_fm) *
                                          (2 * (np.fft.fftfreq(len(s_fm)) > 0))))
    inst_phase = np.unwrap(np.angle(analytic_signal))

    # Derivada de la fase → frecuencia instantánea
    inst_freq = np.diff(inst_phase) * Fs / (2 * np.pi)
    inst_freq = np.concatenate(([inst_freq[0]], inst_freq))  # Mantener longitud

    # Remover la portadora
    m_recovered = inst_freq - fc

    # Normalizar
    if np.max(np.abs(m_recovered)) > 0:
        m_recovered = m_recovered / np.max(np.abs(m_recovered))

    return m_recovered


def demodulate_am(s_am, fc, Fs):
    """
    Demodula una señal AM usando detección de envolvente.

    Args:
        s_am: Señal AM
        fc: Frecuencia portadora (Hz)
        Fs: Frecuencia de muestreo (Hz)

    Returns:
        m_recovered: Señal mensaje recuperada (normalizada)
    """
    # Detección de envolvente usando transformada de Hilbert
    analytic_signal = s_am + 1j * np.imag(np.fft.ifft(np.fft.fft(s_am) *
                                          (2 * (np.fft.fftfreq(len(s_am)) > 0))))
    envelope = np.abs(analytic_signal)

    # Remover componente DC
    m_recovered = envelope - np.mean(envelope)

    # Normalizar
    if np.max(np.abs(m_recovered)) > 0:
        m_recovered = m_recovered / np.max(np.abs(m_recovered))

    return m_recovered


# ============================================================================
# INTERFAZ PRINCIPAL
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

    # ========================================================================
    # SIDEBAR - CONTROLES
    # ========================================================================
    with st.sidebar:
        st.header("⚙️ Parámetros de Control")

        st.subheader("📊 Forma de Onda")
        waveform = st.radio(
            "Seleccione el tipo de mensaje:",
            options=["Senoidal", "Cuadrada", "Diente de Sierra", "Triangular"],
            index=0,
            help="Forma de onda de la señal moduladora m(t)",
        )

        st.divider()

        st.subheader("🎛️ Parámetros del Sistema")

        Fs = (
            st.slider(
                "Frecuencia de muestreo (MHz)",
                min_value=1.0,
                max_value=20.0,
                value=10.0,
                step=0.5,
                help="Frecuencia de muestreo de las señales (regla práctica: Fs ≳ 10·fc)",
            )
            * 1_000_000
        )  # Convertir a Hz

        dur = (
            st.slider(
                "Duración de la señal (ms)",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                help="Duración temporal de la señal a visualizar",
            )
            / 1000
        )  # Convertir a segundos

        st.divider()

        st.subheader("📻 Parámetros de Modulación")

        fc = (
            st.slider(
                "Frecuencia portadora fc (MHz)",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Frecuencia de la portadora",
            )
            * 1_000_000
        )  # Convertir a Hz

        fm = st.slider(
            "Frecuencia del mensaje fm (kHz)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Frecuencia de la señal moduladora",
        ) * 1000  # Convertir a Hz

        Am = st.slider(
            "Amplitud del mensaje Am (V)",
            min_value=0.05,
            max_value=5.0,
            value=1.0,
            step=0.05,
            help="Amplitud de la señal moduladora",
        )

        # Modo de control: β o kf directo
        control_mode = st.radio(
            "Modo de control:",
            options=["β (índice)", "kf directo"],
            index=0,
            help="Controlar mediante el índice de modulación β o la sensibilidad kf directamente",
        )

        if control_mode == "β (índice)":
            beta_input = st.slider(
                "Índice de modulación β",
                min_value=0.1,
                max_value=20.0,
                value=5.0,
                step=0.1,
                help="β = Δf / fm. Controla la desviación de frecuencia",
            )
            # Calcular kf a partir de β: β = Δf/fm = (kf·Am)/fm → kf = β·fm/Am
            kf = (beta_input * fm) / Am if Am > 0 else 0.0
        else:  # kf directo
            kf = (
                st.slider(
                    "Sensibilidad de frecuencia kf (kHz/V)",
                    min_value=0.1,
                    max_value=1000.0,
                    value=5.0,
                    step=1.0,
                    help="Constante de sensibilidad del modulador FM",
                )
                * 1000
            )  # Convertir a Hz/V

        H = st.select_slider(
            "Armónicos considerados H (para Carson)",
            options=[1, 3, 5, 7, 9, 11, 13, 15],
            value=1,
            help="Para mensajes no senoidales usamos f_{m,max} = H·fm. H representa la cantidad aproximada de armónicos significativos de la señal moduladora.",
        )

        st.divider()

        # Checkbox para mostrar portadora
        show_carrier = st.checkbox(
            "Mostrar portadora c(t)",
            value=True,
            help="Mostrar la señal portadora sin modular",
        )

        st.divider()

        # Información de fórmulas
        with st.expander("📐 Fórmulas utilizadas"):
            st.markdown("### Fórmulas utilizadas")

            st.write("**Señal portadora**")
            st.latex(r"c(t) = A_c \cos(2\pi f_c t) \text{, con } A_c=1")

            st.write("**Señal moduladora**")
            st.latex(r"x_{\text{sen}}(t)=\sin(2\pi f_m t)")
            st.latex(r"x_{\text{cuad}}(t)=\operatorname{sgn}[\sin(2\pi f_m t)]")
            st.latex(
                r"x_{\text{diente}}(t)=2\!\left(\frac{t}{T}-\left\lfloor\frac{t}{T}+\frac{1}{2}\right\rfloor\right),~T=\frac{1}{f_m}"
            )
            st.latex(
                r"x_{\text{tri}}(t)=2\left|2\!\left(\frac{t}{T}-\left\lfloor\frac{t}{T}+\frac{1}{2}\right\rfloor\right)\right|-1"
            )
            st.latex(r"m(t)=A_m\,x(t)")

            st.write("**Fase FM (Clark S. Hess)**")
            st.latex(r"\phi(t) = 2\pi f_c t + 2\pi k_f \int_0^t m(\tau)\, d\tau")

            st.write("**Señal FM**")
            st.latex(r"s(t) = A_c \cos(\phi(t))")

            st.write("**Frecuencia instantánea**")
            st.latex(r"f_i(t) = \frac{1}{2\pi}\frac{d\phi}{dt} = f_c + k_f m(t)")

            st.write("**Desviación de frecuencia**")
            st.latex(r"\Delta f = k_f \max|m(t)| = k_f A_m")

            st.write("**Ancho de banda de Carson (mensaje no senoidal)**")
            st.latex(r"f_{m,\max} = H f_m,\quad B \approx 2(\Delta f + f_{m,\max})")

            st.write("**Índice de modulación**")
            st.latex(r"\beta = \frac{\Delta f}{f_m}")

    # ========================================================================
    # CÓMPUTO DE SEÑALES
    # ========================================================================

    # Generar vector de tiempo
    N = int(Fs * dur)
    t = np.linspace(0, dur, N, endpoint=False)
    dt = 1.0 / Fs

    # Generar señal moduladora según forma de onda seleccionada
    if waveform == "Senoidal":
        m_norm = sine_wave(t, fm)
    elif waveform == "Cuadrada":
        m_norm = square_wave(t, fm)
    elif waveform == "Diente de Sierra":
        m_norm = sawtooth_wave(t, fm)
    else:  # Triangular
        m_norm = triangle_wave(t, fm)

    # Escalar por amplitud
    m = Am * m_norm

    # Generar señal portadora (si se requiere mostrar)
    if show_carrier:
        c = np.cos(2 * np.pi * fc * t)

    # Calcular parámetros de modulación FM (con robustez numérica)
    Delta_f = kf * np.max(np.abs(m))  # Hz (desviación de frecuencia)
    beta = (
        Delta_f / fm if fm > 0 else np.inf
    )  # Índice de modulación (evitar división por cero)
    fm_max = H * fm  # Hz (frecuencia máxima considerando armónicos)
    B_carson = 2.0 * (Delta_f + fm_max)  # Hz (ancho de banda de Carson)

    # Fase y señal FM
    phi = 2 * np.pi * fc * t + 2 * np.pi * kf * np.cumsum(m) * dt
    s = np.cos(phi)

    # Frecuencia instantánea
    fi = fc + kf * m  # Hz

    # ========================================================================
    # VALIDACIONES DE MUESTREO (anti-alias)
    # ========================================================================

    # Validación 1: Nyquist mejorado (fc + Δf debe ser < Fs/2)
    nyquist_ok = (fc + Delta_f) < (Fs / 2)
    if not nyquist_ok:
        st.error(
            f"🚫 Alias: fc + Δf = {(fc + Delta_f) / 1000:.2f} kHz ≥ Fs/2 = {(Fs / 2) / 1000:.2f} kHz. "
            "Sube Fs o baja fc/kf/Am."
        )
    elif Fs < 10 * fc:
        st.warning(
            "ℹ️ Sugerencia: usa Fs ≳ 10·fc para una visualización temporal más estable."
        )

    # Validación 2: Muestras por período del mensaje
    mpp = Fs / fm  # muestras por período
    if mpp < 10:
        st.info(
            f"ℹ️ Advertencia: solo {mpp:.1f} muestras por período de m(t). "
            "Aumenta Fs o reduce fm para obtener una visualización más suave."
        )

    # ========================================================================
    # MÉTRICAS PRINCIPALES
    # ========================================================================

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

    with col_m1:
        st.metric(
            label="🎯 Desviación de frecuencia",
            value=f"{Delta_f / 1000:.2f} kHz",
            help="Δf = kf · max|m(t)|",
        )

    with col_m2:
        st.metric(
            label="📏 Ancho de banda (Carson)",
            value=f"{B_carson / 1000:.2f} kHz",
            help="Para mensajes no senoidales usamos f_{m,max} = H·fm. H representa la cantidad aproximada de armónicos significativos de la señal moduladora.",
        )

    with col_m3:
        st.metric(
            label="📡 Frecuencia portadora",
            value=f"{fc / 1_000_000:.2f} MHz",
            help="Frecuencia central de la señal FM",
        )

    with col_m4:
        st.metric(
            label="🎵 Frecuencia del mensaje",
            value=f"{fm / 1000:.2f} kHz",
            help="Frecuencia de la señal moduladora",
        )

    with col_m5:
        st.metric(
            label="📊 Índice de modulación β",
            value=f"{beta:.2f}" if beta != np.inf else "∞",
            help="β = Δf / fm",
        )

    st.divider()

    # ========================================================================
    # PESTAÑAS DE VISUALIZACIÓN
    # ========================================================================

    tabs = st.tabs(["⏱️ Tiempo", "📊 Espectro", "🔧 Demodulación"])

    # ========================================================================
    # TAB 1: TIEMPO - GRÁFICAS (orden pedagógico: m(t) → fi(t) → s(t) → c(t))
    # ========================================================================

    with tabs[0]:
        # Configuración de matplotlib para gráficas más limpias
        plt.style.use("seaborn-v0_8-darkgrid")
        t_ms = t * 1000  # Tiempo en ms

        # --- Gráfica 1: Señal Moduladora m(t) ---
        st.subheader("1️⃣ Señal Moduladora m(t)")
        fig1, ax1 = plt.subplots(figsize=(12, 3))
        ax1.plot(t_ms, m, color="#1f77b4", linewidth=2, label="m(t)")
        ax1.set_xlabel("Tiempo [ms]", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Amplitud [V]", fontsize=11, fontweight="bold")
        ax1.set_title(
            f"Señal Moduladora: {waveform}", fontsize=12, fontweight="bold", pad=10
        )
        ax1.grid(True, alpha=0.3, linestyle="--")
        ax1.set_xlim([0, dur * 1000])
        ax1.legend(loc="upper right")
        st.pyplot(fig1)
        plt.close()

        # --- Gráfica 2: Frecuencia Instantánea fi(t) ---
        st.subheader("2️⃣ Frecuencia Instantánea fi(t) = fc + kf·m(t)")
        fig2, ax2 = plt.subplots(figsize=(12, 3))
        ax2.plot(
            t_ms, fi / 1_000_000, color="#2ca02c", linewidth=2, label="fi(t) = fc + kf·m(t)"
        )
        ax2.axhline(
            fc / 1_000_000,
            color="black",
            linestyle="--",
            linewidth=1.5,
            alpha=0.6,
            label=f"fc = {fc / 1_000_000:.2f} MHz",
        )
        ax2.fill_between(t_ms, fc / 1_000_000, fi / 1_000_000, alpha=0.2, color="#2ca02c")
        ax2.set_xlabel("Tiempo [ms]", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Frecuencia [MHz]", fontsize=11, fontweight="bold")
        ax2.set_title(
            "Frecuencia Instantánea fi(t) = fc + kf·m(t)",
            fontsize=12,
            fontweight="bold",
            pad=10,
        )
        ax2.grid(True, alpha=0.3, linestyle="--")
        ax2.set_xlim([0, dur * 1000])
        ax2.legend(loc="upper right")
        st.pyplot(fig2)
        plt.close()

        # --- Gráfica 3: Señal FM s(t) = cos(ϕ(t)) ---
        st.subheader("3️⃣ Señal FM s(t) = cos(ϕ(t))")

        # Calcular ventana de tiempo para ver la modulación
        # Mostrar 3 periodos del mensaje para ver la variación de frecuencia
        periodo_mensaje = 1.0 / fm  # segundos
        ventana_fm_ms = min(3 * periodo_mensaje * 1000, dur * 1000)  # 3 ciclos del mensaje

        # Encontrar índices
        idx_fm_max = np.searchsorted(t_ms, ventana_fm_ms)

        fig3, ax3 = plt.subplots(figsize=(12, 3))
        ax3.plot(
            t_ms[:idx_fm_max], s[:idx_fm_max], color="#d62728",
            linewidth=1.2, alpha=0.9, label="s(t) = cos(ϕ(t))"
        )
        ax3.set_xlabel("Tiempo [ms]", fontsize=11, fontweight="bold")
        ax3.set_ylabel("Amplitud", fontsize=11, fontweight="bold")
        ax3.set_title(
            f"Señal FM (zoom): s(t) = cos(ϕ(t)), mostrando ~3 ciclos de m(t)",
            fontsize=12, fontweight="bold", pad=10
        )
        ax3.grid(True, alpha=0.3, linestyle="--")
        ax3.set_xlim([0, ventana_fm_ms])
        ax3.set_ylim([-1.2, 1.2])
        ax3.legend(loc="upper right")

        # Nota informativa
        ciclos_portadora_mostrados = fc * ventana_fm_ms / 1000
        st.caption(f"ℹ️ Mostrando los primeros {ventana_fm_ms:.2f} ms "
                  f"(~{ciclos_portadora_mostrados:.0f} ciclos de portadora modulados por 3 ciclos de m(t)). "
                  f"La frecuencia varía entre {(fc-Delta_f)/1e6:.3f} MHz y {(fc+Delta_f)/1e6:.3f} MHz.")

        st.pyplot(fig3)
        plt.close()

        # --- Gráfica 4 (Opcional): Señal Portadora c(t) ---
        if show_carrier:
            st.subheader("4️⃣ Señal Portadora c(t) = cos(2π·fc·t)")

            # Calcular ventana de tiempo apropiada para visualizar la portadora
            # Mostrar aprox. 50 ciclos de la portadora para que se vea claramente
            periodo_portadora = 1.0 / fc  # segundos
            ventana_tiempo = 50 * periodo_portadora  # mostrar ~50 ciclos
            ventana_tiempo_ms = ventana_tiempo * 1000  # convertir a ms

            # Asegurar que no exceda la duración total
            ventana_tiempo_ms = min(ventana_tiempo_ms, dur * 1000)

            # Encontrar índices para esta ventana
            idx_max = np.searchsorted(t_ms, ventana_tiempo_ms)

            fig4, ax4 = plt.subplots(figsize=(12, 3))
            ax4.plot(
                t_ms[:idx_max],
                c[:idx_max],
                color="#ff7f0e",
                linewidth=1.5,
                alpha=0.9,
                label=f"c(t) = cos(2π·fc·t), mostrando ~50 ciclos",
            )
            ax4.set_xlabel("Tiempo [ms]", fontsize=11, fontweight="bold")
            ax4.set_ylabel("Amplitud", fontsize=11, fontweight="bold")
            ax4.set_title(
                f"Señal Portadora (zoom): fc = {fc / 1_000_000:.2f} MHz, T = {periodo_portadora*1e6:.2f} µs",
                fontsize=12,
                fontweight="bold",
                pad=10,
            )
            ax4.grid(True, alpha=0.3, linestyle="--")
            ax4.set_xlim([0, ventana_tiempo_ms])
            ax4.set_ylim([-1.2, 1.2])
            ax4.legend(loc="upper right")

            # Nota informativa
            st.caption(f"ℹ️ Mostrando los primeros {ventana_tiempo_ms:.4f} ms de la señal "
                      f"(~50 ciclos de {periodo_portadora*1e6:.2f} µs cada uno). "
                      f"Con fc = {fc/1e6:.1f} MHz, hay {fc*dur:.0f} ciclos en total.")

            st.pyplot(fig4)
            plt.close()

    # ========================================================================
    # TAB 2: ESPECTRO - ANÁLISIS DE FRECUENCIAS
    # ========================================================================

    with tabs[1]:
        st.markdown("### 📊 Análisis Espectral de Frecuencias")

        # Calcular espectros con rangos apropiados para cada señal
        # Para m(t): mostrar hasta ~20x fm para capturar armónicos
        max_freq_m = fm * 20  # Rango apropiado para mensaje
        # Para s(t): mostrar alrededor de fc ± ancho de banda
        max_freq_s = fc + B_carson * 2  # Rango apropiado para FM

        freqs_m, mag_m, mag_m_db = compute_spectrum(m, Fs, max_freq=max_freq_m)
        freqs_s, mag_s, mag_s_db = compute_spectrum(s, Fs, max_freq=max_freq_s)

        col1, col2 = st.columns(2)

        with col1:
            # Espectro del mensaje m(t)
            st.subheader("Espectro de m(t)")
            fig_spec_m, ax_spec_m = plt.subplots(figsize=(10, 4))
            ax_spec_m.plot(freqs_m / 1000, mag_m_db, color="#1f77b4", linewidth=2)

            # Marcar la frecuencia fundamental
            ax_spec_m.axvline(fm / 1000, color="red", linestyle="--", linewidth=1.5,
                             alpha=0.6, label=f"fm = {fm / 1000:.2f} kHz")

            # Marcar armónicos si no es senoidal
            if waveform != "Senoidal":
                for harmonic in range(3, min(H*2, 10), 2):  # Mostrar algunos armónicos impares
                    if harmonic * fm < max_freq_m:
                        ax_spec_m.axvline(harmonic * fm / 1000, color="orange",
                                        linestyle=":", linewidth=1, alpha=0.4)

            ax_spec_m.set_xlabel("Frecuencia [kHz]", fontsize=11, fontweight="bold")
            ax_spec_m.set_ylabel("Magnitud [dB]", fontsize=11, fontweight="bold")
            ax_spec_m.set_title(f"Espectro de m(t) - {waveform}", fontsize=12, fontweight="bold")
            ax_spec_m.grid(True, alpha=0.3, linestyle="--")
            ax_spec_m.set_xlim([0, max_freq_m / 1000])
            ax_spec_m.legend(loc="upper right")
            st.pyplot(fig_spec_m)
            plt.close()

        with col2:
            # Espectro de la señal FM s(t)
            st.subheader("Espectro de s(t) FM")
            fig_spec_s, ax_spec_s = plt.subplots(figsize=(10, 4))
            ax_spec_s.plot(freqs_s / 1_000_000, mag_s_db, color="#d62728", linewidth=1.5)

            # Marcar fc y bandas laterales
            ax_spec_s.axvline(fc / 1_000_000, color="black", linestyle="--", linewidth=1.5,
                             alpha=0.6, label=f"fc = {fc / 1_000_000:.2f} MHz")
            ax_spec_s.axvline((fc - B_carson/2) / 1_000_000, color="green", linestyle=":",
                             linewidth=1, alpha=0.5, label=f"±B/2 (Carson)")
            ax_spec_s.axvline((fc + B_carson/2) / 1_000_000, color="green", linestyle=":",
                             linewidth=1, alpha=0.5)

            ax_spec_s.set_xlabel("Frecuencia [MHz]", fontsize=11, fontweight="bold")
            ax_spec_s.set_ylabel("Magnitud [dB]", fontsize=11, fontweight="bold")
            ax_spec_s.set_title("Espectro de la Señal FM", fontsize=12, fontweight="bold")
            ax_spec_s.grid(True, alpha=0.3, linestyle="--")
            ax_spec_s.set_xlim([0, max_freq_s / 1_000_000])
            ax_spec_s.legend(loc="upper right", fontsize=9)
            st.pyplot(fig_spec_s)
            plt.close()

        # Información del ancho de banda
        st.info(f"📏 Ancho de banda teórico (Carson): {B_carson / 1000:.2f} kHz "
                f"≈ {B_carson / 1_000_000:.4f} MHz")

    # ========================================================================
    # TAB 3: DEMODULACIÓN - COMPARACIÓN FM vs AM CON RUIDO
    # ========================================================================

    with tabs[2]:
        st.markdown("### 🔧 Demodulación y Análisis de Ruido")

        # Explicación educativa del SNR
        st.info(
            "📡 **SNR (Relación Señal-Ruido)**: Mide qué tan fuerte es la señal comparada con el ruido.\n\n"
            "- **SNR alto** (ej: 30-40 dB): Señal fuerte, ruido débil → ✅ Excelente calidad\n"
            "- **SNR medio** (ej: 15-25 dB): Señal y ruido balanceados → ⚠️ Calidad aceptable\n"
            "- **SNR bajo** (ej: 0-10 dB): Señal débil, ruido fuerte → ❌ Mala calidad"
        )

        # Control de SNR más prominente
        st.markdown("### 🎚️ Control de Relación Señal-Ruido (SNR)")

        col_snr1, col_snr2 = st.columns([3, 1])
        with col_snr1:
            snr_db = st.slider(
                "Ajuste el nivel de SNR [dB]:",
                min_value=0,
                max_value=100,
                value=20,
                step=1,
                help="Valores más altos = menos ruido = mejor calidad. Prueba variar este valor para ver el efecto. Con SNR > 50 la señal será casi perfecta.",
            )

        with col_snr2:
            # Indicador visual de calidad
            if snr_db >= 25:
                st.success("✅ Excelente")
            elif snr_db >= 15:
                st.warning("⚠️ Buena")
            elif snr_db >= 10:
                st.warning("⚠️ Regular")
            else:
                st.error("❌ Mala")

        st.divider()

        # Generar señal AM para comparación (usando m normalizado)
        s_am = (1 + 0.8 * m_norm) * np.cos(2 * np.pi * fc * t)

        # Agregar ruido AWGN a ambas señales
        signal_power_fm = np.mean(s ** 2)
        signal_power_am = np.mean(s_am ** 2)
        noise_power_fm = signal_power_fm / (10 ** (snr_db / 10))
        noise_power_am = signal_power_am / (10 ** (snr_db / 10))

        noise_fm = np.random.normal(0, np.sqrt(noise_power_fm), len(s))
        noise_am = np.random.normal(0, np.sqrt(noise_power_am), len(s_am))

        s_fm_noisy = s + noise_fm
        s_am_noisy = s_am + noise_am

        # Visualización del efecto del ruido
        st.markdown("### 📊 Efecto del Ruido en la Señal FM")

        col_noise1, col_noise2 = st.columns(2)

        with col_noise1:
            st.markdown("**Señal FM Limpia (sin ruido)**")
            fig_clean, ax_clean = plt.subplots(figsize=(10, 3))
            samples_to_show = min(1000, len(t))
            ax_clean.plot(t_ms[:samples_to_show], s[:samples_to_show],
                         color="#2ca02c", linewidth=1.2, alpha=0.9, label="FM limpia")
            ax_clean.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_clean.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_clean.set_title("Señal FM Original (Sin Ruido)", fontsize=11, fontweight="bold", color="green")
            ax_clean.grid(True, alpha=0.3, linestyle="--")
            ax_clean.legend(loc="upper right", fontsize=9)
            st.pyplot(fig_clean)
            plt.close()

        with col_noise2:
            # Determinar color del título basado en SNR
            if snr_db >= 25:
                title_color = "green"
            elif snr_db >= 15:
                title_color = "orange"
            else:
                title_color = "red"

            st.markdown(f"**Señal FM con Ruido (SNR = {snr_db} dB)**")
            fig_noisy, ax_noisy = plt.subplots(figsize=(10, 3))
            ax_noisy.plot(t_ms[:samples_to_show], s_fm_noisy[:samples_to_show],
                         color="#d62728", linewidth=1.2, alpha=0.8, label=f"FM + ruido (SNR={snr_db}dB)")
            ax_noisy.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_noisy.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_noisy.set_title(f"Señal FM con Ruido (SNR = {snr_db} dB)",
                              fontsize=11, fontweight="bold", color=title_color)
            ax_noisy.grid(True, alpha=0.3, linestyle="--")
            ax_noisy.legend(loc="upper right", fontsize=9)
            st.pyplot(fig_noisy)
            plt.close()

        # Mensaje educativo sobre el efecto observado
        if snr_db >= 30:
            st.success("✅ Con SNR alto, el ruido es casi imperceptible. La señal se mantiene limpia.")
        elif snr_db >= 15:
            st.info("ℹ️ Con SNR medio, se observa ruido pero la señal aún es distinguible.")
        else:
            st.warning("⚠️ Con SNR bajo, el ruido es muy evidente y puede degradar significativamente la señal.")

        st.divider()

        # Demodular ambas señales
        m_fm_recovered = demodulate_fm(s_fm_noisy, fc, Fs)
        m_am_recovered = demodulate_am(s_am_noisy, fc, Fs)

        # Calcular MSE (Mean Squared Error) como métrica de calidad
        mse_fm = np.mean((m_norm - m_fm_recovered) ** 2)
        mse_am = np.mean((m_norm - m_am_recovered) ** 2)

        # Comparación FM vs AM
        st.markdown("### 🔬 Comparación: Demodulación FM vs AM")

        # Mostrar métricas de comparación
        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1:
            st.metric(
                label="SNR aplicado",
                value=f"{snr_db} dB",
                help="Relación señal-ruido configurada",
            )
        with col_d2:
            # Calcular mejora relativa
            if mse_am > 0:
                mejora_pct = ((mse_am - mse_fm) / mse_am) * 100
            else:
                mejora_pct = 0

            st.metric(
                label="MSE FM",
                value=f"{mse_fm:.4f}",
                delta=f"{mejora_pct:+.1f}% vs AM" if mejora_pct != 0 else "0%",
                delta_color="inverse",
                help="Error cuadrático medio de FM (menor es mejor)",
            )
        with col_d3:
            st.metric(
                label="MSE AM",
                value=f"{mse_am:.4f}",
                help="Error cuadrático medio de AM (menor es mejor)",
            )
        with col_d4:
            # Mostrar el ganador
            if mse_fm < mse_am:
                st.metric(label="Ganador", value="FM", delta="Mejor", delta_color="normal")
            else:
                st.metric(label="Ganador", value="AM", delta="Mejor", delta_color="normal")

        st.divider()

        # Gráficas de comparación
        col_left, col_right = st.columns(2)

        with col_left:
            # Demodulación FM
            st.subheader("Demodulación FM")

            # Señal con ruido
            fig_fm1, ax_fm1 = plt.subplots(figsize=(10, 3))
            ax_fm1.plot(t_ms[:500], s_fm_noisy[:500], color="#d62728", linewidth=1, alpha=0.7,
                       label=f"FM con ruido (SNR={snr_db}dB)")
            ax_fm1.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_fm1.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_fm1.set_title("Señal FM con Ruido", fontsize=11, fontweight="bold")
            ax_fm1.grid(True, alpha=0.3, linestyle="--")
            ax_fm1.legend(loc="upper right", fontsize=8)
            st.pyplot(fig_fm1)
            plt.close()

            # Señal demodulada
            fig_fm2, ax_fm2 = plt.subplots(figsize=(10, 3))
            ax_fm2.plot(t_ms, m_norm, color="#1f77b4", linewidth=2, alpha=0.7, label="Original m(t)")
            ax_fm2.plot(t_ms, m_fm_recovered, color="#d62728", linewidth=1.5, alpha=0.9,
                       label="Recuperada FM")
            ax_fm2.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_fm2.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_fm2.set_title("Comparación: Original vs Demodulada FM", fontsize=11, fontweight="bold")
            ax_fm2.grid(True, alpha=0.3, linestyle="--")
            ax_fm2.legend(loc="upper right", fontsize=8)
            st.pyplot(fig_fm2)
            plt.close()

        with col_right:
            # Demodulación AM
            st.subheader("Demodulación AM")

            # Señal con ruido
            fig_am1, ax_am1 = plt.subplots(figsize=(10, 3))
            ax_am1.plot(t_ms[:500], s_am_noisy[:500], color="#2ca02c", linewidth=1, alpha=0.7,
                       label=f"AM con ruido (SNR={snr_db}dB)")
            ax_am1.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_am1.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_am1.set_title("Señal AM con Ruido", fontsize=11, fontweight="bold")
            ax_am1.grid(True, alpha=0.3, linestyle="--")
            ax_am1.legend(loc="upper right", fontsize=8)
            st.pyplot(fig_am1)
            plt.close()

            # Señal demodulada
            fig_am2, ax_am2 = plt.subplots(figsize=(10, 3))
            ax_am2.plot(t_ms, m_norm, color="#1f77b4", linewidth=2, alpha=0.7, label="Original m(t)")
            ax_am2.plot(t_ms, m_am_recovered, color="#2ca02c", linewidth=1.5, alpha=0.9,
                       label="Recuperada AM")
            ax_am2.set_xlabel("Tiempo [ms]", fontsize=10, fontweight="bold")
            ax_am2.set_ylabel("Amplitud", fontsize=10, fontweight="bold")
            ax_am2.set_title("Comparación: Original vs Demodulada AM", fontsize=11, fontweight="bold")
            ax_am2.grid(True, alpha=0.3, linestyle="--")
            ax_am2.legend(loc="upper right", fontsize=8)
            st.pyplot(fig_am2)
            plt.close()

        st.divider()

        # Conclusión educativa
        st.markdown("### 📝 Conclusión del Análisis")

        if mse_fm < mse_am:
            mejora = ((mse_am - mse_fm) / mse_am) * 100
            st.success(
                f"✅ **FM tiene mejor desempeño que AM** con SNR = {snr_db} dB\n\n"
                f"- MSE FM: {mse_fm:.4f}\n"
                f"- MSE AM: {mse_am:.4f}\n"
                f"- Mejora: {mejora:.1f}% menos error con FM\n\n"
                f"**¿Por qué FM es más robusto?** La información en FM está codificada en la frecuencia "
                f"de la portadora, no en su amplitud. El ruido AWGN afecta principalmente la amplitud, "
                f"por lo que FM es más resistente al ruido que AM."
            )
        else:
            st.warning(
                f"⚠️ **AM tiene mejor desempeño que FM** con SNR = {snr_db} dB\n\n"
                f"- MSE AM: {mse_am:.4f}\n"
                f"- MSE FM: {mse_fm:.4f}\n\n"
                f"**Nota**: Esto puede ocurrir con SNR muy alto donde ambos sistemas funcionan bien, "
                f"o con parámetros específicos de la modulación."
            )

        # Recomendaciones para experimentar
        with st.expander("💡 Prueba estos experimentos"):
            st.markdown("""
            **Experimenta variando el SNR para observar cómo cambia la calidad:**

            1. **SNR = 5 dB** (ruido fuerte):
               - Observa cómo la señal se degrada significativamente
               - Nota la diferencia FM vs AM

            2. **SNR = 15 dB** (ruido moderado):
               - Nivel típico en comunicaciones reales
               - FM debería mostrar ventaja sobre AM

            3. **SNR = 30 dB** (ruido bajo):
               - Ambos sistemas funcionan bien
               - Diferencia es menos pronunciada

            4. **Varía β (en sidebar)** y observa:
               - β alto = más ancho de banda = más robusto al ruido
               - β bajo = menos ancho de banda = más susceptible al ruido

            **Observa que:** Al aumentar el SNR (más señal, menos ruido), la calidad mejora.
            Al disminuir el SNR (menos señal, más ruido), la calidad empeora.
            """)

    # ========================================================================
    # INFORMACIÓN ADICIONAL
    # ========================================================================

    st.divider()

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


# ============================================================================
# EJECUTAR
# ============================================================================

if __name__ == "__main__":
    main()
