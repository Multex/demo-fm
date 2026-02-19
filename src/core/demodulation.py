"""
Funciones de demodulación para FM y AM.
"""
import numpy as np


def demodulate_fm(s_fm: np.ndarray, fc: float, Fs: float) -> np.ndarray:
    """
    Demodula una señal FM usando diferenciación de fase.

    Args:
        s_fm: Señal FM
        fc: Frecuencia portadora (Hz)
        Fs: Frecuencia de muestreo (Hz)

    Returns:
        Señal mensaje recuperada (normalizada)
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


def demodulate_am(s_am: np.ndarray, fc: float, Fs: float) -> np.ndarray:
    """
    Demodula una señal AM usando detección de envolvente.

    Args:
        s_am: Señal AM
        fc: Frecuencia portadora (Hz)
        Fs: Frecuencia de muestreo (Hz)

    Returns:
        Señal mensaje recuperada (normalizada)
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
