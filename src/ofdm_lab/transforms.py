"""Transformées unitaires sur le dernier axe, ordre fréquentiel natif NumPy."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .noise import _finite_real, _positive_integer


def _finite_array(values: ArrayLike) -> NDArray[np.complex128]:
    result = np.asarray(values, dtype=np.complex128)
    if result.ndim == 0 or result.size == 0 or not np.all(np.isfinite(result)):
        raise ValueError("Le signal doit être un tableau non vide, fini, avec au moins un axe.")
    return result


def fft(values: ArrayLike) -> NDArray[np.complex128]:
    """DFT unitaire : X[k]=sum_n x[n] exp(-j2πkn/N)/sqrt(N), dernier axe."""
    return np.fft.fft(_finite_array(values), axis=-1, norm="ortho")


def ifft(values: ArrayLike) -> NDArray[np.complex128]:
    """DFT inverse unitaire, signe + ; conserve somme|X|²=somme|x|²."""
    return np.fft.ifft(_finite_array(values), axis=-1, norm="ortho")


def subcarrier_frequencies(n_fft: int, spacing_hz: float) -> NDArray[np.float64]:
    """Fréquences [Hz] en ordre natif : DC, positives, Nyquist négative, négatives."""
    size = _positive_integer(n_fft, "La taille FFT")
    spacing = _finite_real(spacing_hz, "L'espacement des sous-porteuses")
    if spacing <= 0 or not np.isfinite(size * spacing):
        raise ValueError("L'espacement doit être positif et la fréquence d'échantillonnage finie.")
    return np.fft.fftfreq(size, d=1 / (size * spacing))
