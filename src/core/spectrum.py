"""
Análisis espectral de señales.
"""
import numpy as np


def compute_spectrum(signal: np.ndarray, Fs: float, max_freq: float = None):
    """
    Calcula el espectro de frecuencias (FFT) de una señal.

    Args:
        signal: Señal de entrada
        Fs: Frecuencia de muestreo (Hz)
        max_freq: Frecuencia máxima a mostrar (Hz). Si es None, muestra todo.

    Returns:
        tuple: (freqs, magnitude, magnitude_db)
            - freqs: Vector de frecuencias (Hz)
            - magnitude: Magnitud del espectro (escala lineal)
            - magnitude_db: Magnitud en dB
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
