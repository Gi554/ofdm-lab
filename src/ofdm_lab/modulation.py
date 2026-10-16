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


def _qam_parameters(order: int) -> tuple[int, int, float]:
    """Nombre de bits par axe, niveaux par axe et facteur de normalisation."""
    if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or order not in (16, 64):
        raise ValueError("L'ordre QAM doit être l'entier 16 ou 64.")
    axis_bits = (int(order).bit_length() - 1) // 2
    return axis_bits, 2**axis_bits, float(np.sqrt(2 * (order - 1) / 3))


def modulate_qam(bits: ArrayLike, order: int) -> NDArray[np.complex128]:
    """QAM carrée Gray, Es=1 sur l'alphabet équiprobable ; bits I puis Q, MSB en tête.

    Pour un axe 16-QAM : 00 -> +3, 01 -> +1, 11 -> -1, 10 -> -3,
    avant division des deux composantes par sqrt(10). Aucun bourrage implicite.
    """
    axis_bits, levels, scale = _qam_parameters(order)
    values = validate_bits(bits)
    if values.size % (2 * axis_bits):
        raise ValueError(f"La {order}-QAM exige un multiple de {2 * axis_bits} bits.")
    groups = values.reshape(-1, 2, axis_bits)
    weights = 1 << np.arange(axis_bits - 1, -1, -1)
    gray = np.sum(groups * weights, axis=2)
    position = gray.copy()
    for shift in range(1, axis_bits):
        position ^= gray >> shift
    amplitudes = (levels - 1 - 2 * position) / scale
    return amplitudes[:, 0] + 1j * amplitudes[:, 1]
