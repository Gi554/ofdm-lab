"""Décisions dures cohérentes : synchronisation de phase supposée parfaite."""

import numpy as np
from numpy.typing import ArrayLike, NDArray


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
