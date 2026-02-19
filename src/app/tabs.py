"""
Pestañas de visualización de la app.
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from core.fm_calculator import FMParameters
from core.spectrum import compute_spectrum
from core.demodulation import demodulate_fm, demodulate_am
from core.fm_calculator import calculate_am_signal
from .components import render_snr_quality_indicator


def render_time_tab(t: np.ndarray, m: np.ndarray, s: np.ndarray, fi: np.ndarray,
                    c: np.ndarray, params: FMParameters, show_carrier: bool):
    """
    Renderiza la pestaña de visualización en tiempo.
    
    Args:
        t: Vector de tiempo
        m: Señal moduladora
        s: Señal FM
        fi: Frecuencia instantánea
        c: Señal portadora
        params: Parámetros FM
        show_carrier: Si se debe mostrar la portadora
    """
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
        f"Señal Moduladora", fontsize=12, fontweight="bold", pad=10
    )
    ax1.grid(True, alpha=0.3, linestyle="--")
    ax1.set_xlim([0, t[-1] * 1000])
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
        params.fc / 1_000_000,
        color="black",
        linestyle="--",
        linewidth=1.5,
        alpha=0.6,
        label=f"fc = {params.fc_mhz:.2f} MHz",
    )
    ax2.fill_between(t_ms, params.fc / 1_000_000, fi / 1_000_000, alpha=0.2, color="#2ca02c")
    ax2.set_xlabel("Tiempo [ms]", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Frecuencia [MHz]", fontsize=11, fontweight="bold")
    ax2.set_title(
        "Frecuencia Instantánea fi(t) = fc + kf·m(t)",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax2.grid(True, alpha=0.3, linestyle="--")
    ax2.set_xlim([0, t[-1] * 1000])
    ax2.legend(loc="upper right")
    st.pyplot(fig2)
    plt.close()

    # --- Gráfica 3: Señal FM s(t) = cos(ϕ(t)) ---
    st.subheader("3️⃣ Señal FM s(t) = cos(ϕ(t))")

    # Calcular ventana de tiempo para ver la modulación
    # Mostrar 3 periodos del mensaje para ver la variación de frecuencia
    periodo_mensaje = 1.0 / params.fm  # segundos
    ventana_fm_ms = min(3 * periodo_mensaje * 1000, t[-1] * 1000)  # 3 ciclos del mensaje

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
    ciclos_portadora_mostrados = params.fc * ventana_fm_ms / 1000
    st.caption(f"ℹ️ Mostrando los primeros {ventana_fm_ms:.2f} ms "
              f"(~{ciclos_portadora_mostrados:.0f} ciclos de portadora modulados por 3 ciclos de m(t)). "
              f"La frecuencia varía entre {(params.fc-params.delta_f)/1e6:.3f} MHz y {(params.fc+params.delta_f)/1e6:.3f} MHz.")

    st.pyplot(fig3)
    plt.close()

    # --- Gráfica 4 (Opcional): Señal Portadora c(t) ---
    if show_carrier:
        st.subheader("4️⃣ Señal Portadora c(t) = cos(2π·fc·t)")

        # Calcular ventana de tiempo apropiada para visualizar la portadora
        # Mostrar aprox. 50 ciclos de la portadora para que se vea claramente
        periodo_portadora = 1.0 / params.fc  # segundos
        ventana_tiempo = 50 * periodo_portadora  # mostrar ~50 ciclos
        ventana_tiempo_ms = ventana_tiempo * 1000  # convertir a ms

        # Asegurar que no exceda la duración total
        ventana_tiempo_ms = min(ventana_tiempo_ms, t[-1] * 1000)

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
            f"Señal Portadora (zoom): fc = {params.fc_mhz:.2f} MHz, T = {periodo_portadora*1e6:.2f} µs",
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
                  f"Con fc = {params.fc/1e6:.1f} MHz, hay {params.fc*t[-1]:.0f} ciclos en total.")

        st.pyplot(fig4)
        plt.close()


def render_spectrum_tab(m: np.ndarray, s: np.ndarray, params: FMParameters, Fs: float, waveform: str):
    """
    Renderiza la pestaña de análisis espectral.
    
    Args:
        m: Señal moduladora
        s: Señal FM
        params: Parámetros FM
        Fs: Frecuencia de muestreo
        waveform: Tipo de onda
    """
    st.markdown("### 📊 Análisis Espectral de Frecuencias")

    # Calcular espectros con rangos apropiados para cada señal
    # Para m(t): mostrar hasta ~20x fm para capturar armónicos
    max_freq_m = params.fm * 20  # Rango apropiado para mensaje
    # Para s(t): mostrar alrededor de fc ± ancho de banda
    max_freq_s = params.fc + params.B_carson * 2  # Rango apropiado para FM

    freqs_m, mag_m, mag_m_db = compute_spectrum(m, Fs, max_freq=max_freq_m)
    freqs_s, mag_s, mag_s_db = compute_spectrum(s, Fs, max_freq=max_freq_s)

    col1, col2 = st.columns(2)

    with col1:
        # Espectro del mensaje m(t)
        st.subheader("Espectro de m(t)")
        fig_spec_m, ax_spec_m = plt.subplots(figsize=(10, 4))
        ax_spec_m.plot(freqs_m / 1000, mag_m_db, color="#1f77b4", linewidth=2)

        # Marcar la frecuencia fundamental
        ax_spec_m.axvline(params.fm / 1000, color="red", linestyle="--", linewidth=1.5,
                         alpha=0.6, label=f"fm = {params.fm_khz:.2f} kHz")

        # Marcar armónicos si no es senoidal
        if waveform != "Senoidal":
            for harmonic in range(3, min(params.H*2, 10), 2):  # Mostrar algunos armónicos impares
                if harmonic * params.fm < max_freq_m:
                    ax_spec_m.axvline(harmonic * params.fm / 1000, color="orange",
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
        ax_spec_s.axvline(params.fc / 1_000_000, color="black", linestyle="--", linewidth=1.5,
                         alpha=0.6, label=f"fc = {params.fc_mhz:.2f} MHz")
        ax_spec_s.axvline((params.fc - params.B_carson/2) / 1_000_000, color="green", linestyle=":",
                         linewidth=1, alpha=0.5, label=f"±B/2 (Carson)")
        ax_spec_s.axvline((params.fc + params.B_carson/2) / 1_000_000, color="green", linestyle=":",
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
    st.info(f"📏 Ancho de banda teórico (Carson): {params.B_carson_khz:.2f} kHz "
            f"≈ {params.B_carson / 1_000_000:.4f} MHz")


def render_demodulation_tab(t: np.ndarray, m_norm: np.ndarray, s: np.ndarray, 
                            params: FMParameters, Fs: float):
    """
    Renderiza la pestaña de demodulación y comparación FM vs AM.
    
    Args:
        t: Vector de tiempo
        m_norm: Señal moduladora normalizada
        s: Señal FM
        params: Parámetros FM
        Fs: Frecuencia de muestreo
    """
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
        render_snr_quality_indicator(snr_db)

    st.divider()

    # Generar señal AM para comparación
    s_am = calculate_am_signal(t, params.fc, m_norm)

    # Agregar ruido AWGN a ambas señales
    signal_power_fm = np.mean(s ** 2)
    signal_power_am = np.mean(s_am ** 2)
    noise_power_fm = signal_power_fm / (10 ** (snr_db / 10))
    noise_power_am = signal_power_am / (10 ** (snr_db / 10))

    np.random.seed(42)  # Para reproducibilidad
    noise_fm = np.random.normal(0, np.sqrt(noise_power_fm), len(s))
    noise_am = np.random.normal(0, np.sqrt(noise_power_am), len(s_am))

    s_fm_noisy = s + noise_fm
    s_am_noisy = s_am + noise_am

    t_ms = t * 1000

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
    m_fm_recovered = demodulate_fm(s_fm_noisy, params.fc, Fs)
    m_am_recovered = demodulate_am(s_am_noisy, params.fc, Fs)

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
