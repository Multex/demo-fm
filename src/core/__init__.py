"""
Core functionality for FM modulation demo.
"""
from .waveforms import generate_message, WAVEFORM_GENERATORS
from .spectrum import compute_spectrum
from .demodulation import demodulate_fm, demodulate_am
from .fm_calculator import FMParameters, calculate_fm_signal, calculate_carrier, calculate_am_signal
from .validations import validate_nyquist, validate_samples_per_period, ValidationResult

__all__ = [
    "generate_message",
    "WAVEFORM_GENERATORS",
    "compute_spectrum",
    "demodulate_fm",
    "demodulate_am",
    "FMParameters",
    "calculate_fm_signal",
    "calculate_carrier",
    "calculate_am_signal",
    "validate_nyquist",
    "validate_samples_per_period",
    "ValidationResult",
]
