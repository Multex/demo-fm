"""
Validaciones para parámetros de muestreo y señales.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Resultado de una validación."""
    is_valid: bool
    message: str
    level: str  # "error", "warning", "info"


def validate_nyquist(fc: float, delta_f: float, Fs: float) -> ValidationResult:
    """
    Valida el criterio de Nyquist mejorado para FM.
    
    Args:
        fc: Frecuencia portadora (Hz)
        delta_f: Desviación de frecuencia (Hz)
        Fs: Frecuencia de muestreo (Hz)
    
    Returns:
        ValidationResult con el estado de la validación
    """
    nyquist_ok = (fc + delta_f) < (Fs / 2)
    
    if not nyquist_ok:
        return ValidationResult(
            is_valid=False,
            message=f"🚫 Alias: fc + Δf = {(fc + delta_f) / 1000:.2f} kHz ≥ Fs/2 = {(Fs / 2) / 1000:.2f} kHz. "
                    "Sube Fs o baja fc/kf/Am.",
            level="error"
        )
    
    if Fs < 10 * fc:
        return ValidationResult(
            is_valid=True,
            message="ℹ️ Sugerencia: usa Fs ≳ 10·fc para una visualización temporal más estable.",
            level="warning"
        )
    
    return ValidationResult(is_valid=True, message="", level="ok")


def validate_samples_per_period(Fs: float, fm: float, min_samples: float = 10.0) -> Optional[ValidationResult]:
    """
    Valida que haya suficientes muestras por período del mensaje.
    
    Args:
        Fs: Frecuencia de muestreo (Hz)
        fm: Frecuencia del mensaje (Hz)
        min_samples: Mínimo de muestras recomendadas por período
    
    Returns:
        ValidationResult si hay advertencia, None si está OK
    """
    mpp = Fs / fm  # muestras por período
    
    if mpp < min_samples:
        return ValidationResult(
            is_valid=True,
            message=f"ℹ️ Advertencia: solo {mpp:.1f} muestras por período de m(t). "
                    "Aumenta Fs o reduce fm para obtener una visualización más suave.",
            level="info"
        )
    
    return None
