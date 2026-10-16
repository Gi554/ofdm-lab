"""Mapping cohérent, énergie de constellation Es = 1 (unités normalisées)."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .bits import validate_bits


def modulate_bpsk(bits: ArrayLike) -> NDArray[np.complex128]:
    """BPSK : 0 -> +1 et 1 -> -1. Un bit par symbole."""
    values = validate_bits(bits)
    return (1.0 - 2.0 * values).astype(np.complex128)


def modulate_qpsk(bits: ArrayLike) -> NDArray[np.complex128]:
    """QPSK Gray : (bI,bQ) -> [(1-2bI)+j(1-2bQ)]/sqrt(2)."""
    values = validate_bits(bits)
    if values.size % 2:
        raise ValueError("La QPSK exige un nombre pair de bits ; aucun bourrage implicite.")
    pairs = values.reshape(-1, 2)
    return ((1.0 - 2.0 * pairs[:, 0]) + 1j * (1.0 - 2.0 * pairs[:, 1])) / np.sqrt(2)
