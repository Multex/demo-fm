"""
Cálculos para modulación FM.
"""
import numpy as np


class FMParameters:
    """Parámetros de modulación FM."""
    
    def __init__(self, fc: float, fm: float, Am: float, kf: float, H: int):
        """
        Args:
            fc: Frecuencia portadora (Hz)
            fm: Frecuencia del mensaje (Hz)
            Am: Amplitud del mensaje (V)
            kf: Sensibilidad de frecuencia (Hz/V)
            H: Número de armónicos considerados
        """
        self.fc = fc
        self.fm = fm
        self.Am = Am
        self.kf = kf
        self.H = H
        
        # Cálculos derivados
        self.delta_f = kf * Am  # Desviación de frecuencia (Hz)
        self.beta = self.delta_f / fm if fm > 0 else np.inf  # Índice de modulación
        self.fm_max = H * fm  # Frecuencia máxima considerando armónicos
        self.B_carson = 2.0 * (self.delta_f + self.fm_max)  # Ancho de banda de Carson (Hz)
    
    @property
    def delta_f_khz(self) -> float:
        """Desviación de frecuencia en kHz."""
        return self.delta_f / 1000
    
    @property
    def B_carson_khz(self) -> float:
        """Ancho de banda de Carson en kHz."""
        return self.B_carson / 1000
    
    @property
    def fc_mhz(self) -> float:
        """Frecuencia portadora en MHz."""
        return self.fc / 1_000_000
    
    @property
    def fm_khz(self) -> float:
        """Frecuencia del mensaje en kHz."""
        return self.fm / 1000


def calculate_fm_signal(t: np.ndarray, fc: float, kf: float, m: np.ndarray, dt: float) -> tuple:
    """
    Calcula la señal FM y la frecuencia instantánea.
    
    Args:
        t: Vector de tiempo
        fc: Frecuencia portadora (Hz)
        kf: Sensibilidad de frecuencia (Hz/V)
        m: Señal moduladora
        dt: Paso de tiempo (1/Fs)
    
    Returns:
        tuple: (s, fi, phi)
            - s: Señal FM
            - fi: Frecuencia instantánea
            - phi: Fase instantánea
    """
    # Fase FM: φ(t) = 2πfc·t + 2πkf·∫m(τ)dτ
    phi = 2 * np.pi * fc * t + 2 * np.pi * kf * np.cumsum(m) * dt
    s = np.cos(phi)
    
    # Frecuencia instantánea: fi(t) = fc + kf·m(t)
    fi = fc + kf * m
    
    return s, fi, phi


def calculate_carrier(t: np.ndarray, fc: float) -> np.ndarray:
    """
    Genera la señal portadora.
    
    Args:
        t: Vector de tiempo
        fc: Frecuencia portadora (Hz)
    
    Returns:
        Señal portadora c(t) = cos(2π·fc·t)
    """
    return np.cos(2 * np.pi * fc * t)


def calculate_am_signal(t: np.ndarray, fc: float, m_norm: np.ndarray, modulation_index: float = 0.8) -> np.ndarray:
    """
    Genera una señal AM para comparación.
    
    Args:
        t: Vector de tiempo
        fc: Frecuencia portadora (Hz)
        m_norm: Señal moduladora normalizada (±1)
        modulation_index: Índice de modulación AM (default 0.8)
    
    Returns:
        Señal AM s(t) = (1 + μ·m(t))·cos(2π·fc·t)
    """
    return (1 + modulation_index * m_norm) * np.cos(2 * np.pi * fc * t)
