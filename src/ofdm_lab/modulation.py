"""Mapping cohérent, énergie de constellation Es = 1 (unités normalisées)."""

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .bits import validate_bits


def modulate_bpsk(bits: ArrayLike) -> NDArray[np.complex128]:
    """BPSK : 0 -> +1 et 1 -> -1. Un bit par symbole."""
    values = validate_bits(bits)
    return (1.0 - 2.0 * values).astype(np.complex128)
