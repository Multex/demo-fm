"""
Generadores de señales para modulación FM.
"""
import numpy as np


def square_wave(t: np.ndarray, fm: float) -> np.ndarray:
    """Genera una onda cuadrada normalizada a ±1."""
    return np.sign(np.sin(2 * np.pi * fm * t))


def sawtooth_wave(t: np.ndarray, fm: float) -> np.ndarray:
    """Genera una onda diente de sierra normalizada a ±1."""
    T = 1.0 / fm
    return 2 * ((t / T) - np.floor(0.5 + t / T))


def triangle_wave(t: np.ndarray, fm: float) -> np.ndarray:
    """Genera una onda triangular normalizada a ±1."""
    T = 1.0 / fm
    return 2 * np.abs(2 * ((t / T) - np.floor(0.5 + t / T))) - 1


def sine_wave(t: np.ndarray, fm: float) -> np.ndarray:
    """Genera una onda senoidal normalizada a ±1."""
    return np.sin(2 * np.pi * fm * t)


WAVEFORM_GENERATORS = {
    "Senoidal": sine_wave,
    "Cuadrada": square_wave,
    "Diente de Sierra": sawtooth_wave,
    "Triangular": triangle_wave,
}


def generate_message(t: np.ndarray, fm: float, waveform: str, amplitude: float = 1.0) -> np.ndarray:
    """
    Genera la señal moduladora m(t).
    
    Args:
        t: Vector de tiempo
        fm: Frecuencia del mensaje (Hz)
        waveform: Tipo de onda (Senoidal, Cuadrada, Diente de Sierra, Triangular)
        amplitude: Amplitud Am (V)
    
    Returns:
        Señal moduladora escalada por amplitud
    """
    generator = WAVEFORM_GENERATORS.get(waveform, sine_wave)
    m_norm = generator(t, fm)
    return amplitude * m_norm
