"""Références AWGN cohérentes, symboles équiprobables, phase et timing idéaux."""

import numpy as np
from scipy.special import erfc, ndtr

from .noise import db_to_linear, noise_variance


def _order(order: int) -> int:
    if isinstance(order, (bool, np.bool_)) or not isinstance(order, (int, np.integer)):
        raise ValueError("La modulation doit être l'entier 2, 4, 16 ou 64.")
    if order not in (2, 4, 16, 64):
        raise ValueError("La modulation doit être l'entier 2, 4, 16 ou 64.")
    return int(order)


def q_function(value):
    """Q(x)=P(Z>x), Z gaussienne standard ; évaluation stable par erfc."""
    return 0.5 * erfc(np.asarray(value, dtype=float) / np.sqrt(2))


def ber_awgn(ebn0_db: float, order: int) -> float:
    """BER exact : BPSK/QPSK analytiques, QAM par matrice des transitions 1D Gray.

    La QAM intègre la loi gaussienne sur chaque région de décision, y compris les
    sauts de plusieurs niveaux. L'exactitude est celle du modèle, à l'arrondi numérique près.
    """
    m = _order(order)
    gamma = db_to_linear(ebn0_db)
    if m in (2, 4):
        return float(q_function(np.sqrt(2 * gamma)))
    k = m.bit_length() - 1
    levels = int(np.sqrt(m))
    scale = np.sqrt(2 * (m - 1) / 3)
    coordinates = np.arange(-levels + 1, levels, 2) / scale
    bounds = np.concatenate(([-np.inf], (coordinates[:-1] + coordinates[1:]) / 2, [np.inf]))
    sigma = np.sqrt(noise_variance(ebn0_db, k) / 2)
    standardized = (bounds[None, :] - coordinates[:, None]) / sigma
    low, high = standardized[:, :-1], standardized[:, 1:]
    # Différence de fonctions de survie pour ne pas soustraire deux nombres proches de 1.
    probability = np.where(low >= 0, ndtr(-low) - ndtr(-high), ndtr(high) - ndtr(low))
    position = levels - 1 - np.arange(levels)
    gray = position ^ (position >> 1)
    bits = (gray[:, None] >> np.arange(k // 2 - 1, -1, -1)) & 1
    hamming = np.count_nonzero(bits[:, None, :] != bits[None, :, :], axis=2)
    return float(np.sum(probability * hamming) / (levels * (k // 2)))


def ser_awgn(ebn0_db: float, order: int) -> float:
    """SER exact BPSK et QAM carrée (QPSK incluse) sur AWGN cohérent."""
    m = _order(order)
    gamma = db_to_linear(ebn0_db)
    if m == 2:
        return ber_awgn(ebn0_db, m)
    k = m.bit_length() - 1
    axis_error = 2 * (1 - 1 / np.sqrt(m)) * q_function(np.sqrt(3 * k * gamma / (m - 1)))
    return float(2 * axis_error - axis_error**2)


def qam_ber_nearest_neighbor(ebn0_db: float, order: int) -> float:
    """Approximation Gray de plus proches voisins ; pertinente surtout à SNR élevé."""
    m = _order(order)
    if m not in (16, 64):
        raise ValueError("L'approximation QAM attend 16 ou 64.")
    k = m.bit_length() - 1
    return float(
        4 / k * (1 - 1 / np.sqrt(m)) * q_function(np.sqrt(3 * k * db_to_linear(ebn0_db) / (m - 1)))
    )
