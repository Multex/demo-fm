"""
Panel lateral de controles para la app.
"""
import streamlit as st


def render_sidebar():
    """
    Renderiza el sidebar con todos los controles.
    
    Returns:
        dict: Diccionario con todos los parámetros seleccionados
    """
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
            render_formulas()

    return {
        "waveform": waveform,
        "Fs": Fs,
        "dur": dur,
        "fc": fc,
        "fm": fm,
        "Am": Am,
        "kf": kf,
        "H": H,
        "show_carrier": show_carrier,
    }


def render_formulas():
    """Renderiza las fórmulas matemáticas en el sidebar."""
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
