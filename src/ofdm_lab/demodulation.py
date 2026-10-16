"""Décisions dures cohérentes : synchronisation de phase supposée parfaite."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .modulation import _qam_parameters


def _symbols(symbols: ArrayLike) -> NDArray[np.complex128]:
    values = np.asarray(symbols, dtype=np.complex128)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("Les symboles doivent former un vecteur complexe fini.")
    return values


def demodulate_bpsk(symbols: ArrayLike) -> NDArray[np.uint8]:
    """Décision sur Re(z) ; une valeur exactement nulle décide 0."""
    return (_symbols(symbols).real < 0).astype(np.uint8)


def demodulate_qpsk(symbols: ArrayLike) -> NDArray[np.uint8]:
    """Décisions indépendantes I puis Q ; seuil nul décidé 0."""
    values = _symbols(symbols)
    return np.column_stack((values.real < 0, values.imag < 0)).astype(np.uint8).ravel()


def demodulate_qam(symbols: ArrayLike, order: int) -> NDArray[np.uint8]:
    """Décision au plus proche niveau I/Q ; égalité décidée vers l'amplitude supérieure.

    Les niveaux extrêmes saturent naturellement. Ordre de sortie : bits I puis Q,
    bit de poids fort en tête pour chaque axe.
    """
    axis_bits, levels, scale = _qam_parameters(order)
    values = _symbols(symbols)
    thresholds = np.arange(-levels + 2, levels - 1, 2) / scale
    axes = np.column_stack((values.real, values.imag))
    position = levels - 1 - np.searchsorted(thresholds, axes, side="right")
    gray = position ^ (position >> 1)
    shifts = np.arange(axis_bits - 1, -1, -1)
    return ((gray[..., None] >> shifts) & 1).astype(np.uint8).ravel()
