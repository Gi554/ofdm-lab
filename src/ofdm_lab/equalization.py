"""Égaliseurs diagonaux connus : ZF et LMMSE, avec biais et bruit explicités."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from .noise import _finite_real
from .transforms import _finite_array


@dataclass(frozen=True)
class EqualizationResult:
    """Estimation, gain résiduel G=WH, variance de bruit |W|²N0 et effacements."""

    symbols: np.ndarray
    decision_gain: np.ndarray
    noise_variance_out: np.ndarray
    erasures: np.ndarray
    weights: np.ndarray


def equalize(
    symbols: ArrayLike,
    channel: ArrayLike,
    method: str = "zf",
    noise_variance: float = 0,
    symbol_energy: float = 1,
    minimum_magnitude: float = 1e-12,
) -> EqualizationResult:
    """Estimer X à partir de Y=HX+W avec Es moyen de l'alphabet.

    ZF : 1/H, refus des creux sous le seuil numérique. LMMSE : H*/(|H|²+N0/Es).
    Le LMMSE est biaisé : ses points idéaux valent G X, pas X. Le gain doit être pris
    en compte pour une décision QAM correcte. Un H nul n'est pas inversé artificiellement.
    Le modèle diagonal n'est valide que si le CP couvre la mémoire du canal.
    """
    y = _finite_array(symbols)
    h = np.asarray(channel, dtype=complex)
    if h.size == 0 or not np.all(np.isfinite(h)):
        raise ValueError("La réponse fréquentielle doit être finie et non vide.")
    try:
        h = np.broadcast_to(h, y.shape)
    except ValueError as error:
        raise ValueError("H doit pouvoir se diffuser dans la forme de Y.") from error
    variance = _finite_real(noise_variance, "N0")
    energy = _finite_real(symbol_energy, "Es")
    floor = _finite_real(minimum_magnitude, "Le seuil de module")
    if variance < 0 or energy <= 0 or floor < 0:
        raise ValueError("N0 et le seuil doivent être non négatifs, Es strictement positive.")
    if method not in ("zf", "mmse"):
        raise ValueError("L'égaliseur doit être zf ou mmse.")
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        if method == "zf":
            if np.any(abs(h) <= floor):
                raise ValueError("ZF ne peut pas inverser un creux nul ou sous le seuil numérique.")
            weights = 1 / h
        else:
            denominator = abs(h) ** 2 + variance / energy
            weights = np.divide(h.conj(), denominator, out=np.zeros_like(h), where=denominator > 0)
        gain = np.real(weights * h)
        estimates = weights * y
        noise_out = abs(weights) ** 2 * variance
    if not all(np.all(np.isfinite(value)) for value in [weights, gain, estimates, noise_out]):
        raise ValueError("L'égalisation dépasse la plage numérique représentable.")
    return EqualizationResult(estimates, gain, noise_out, gain <= 0, weights)


def decision_symbols(result: EqualizationResult) -> np.ndarray:
    """Compenser G pour décider dans l'alphabet d'origine ; 0 sur les effacements.

    Hors canal nul, ZF et MMSE avec gain pris en compte produisent les mêmes décisions
    ML scalaires sur AWGN à canal parfaitement connu. Ils n'ont pas la même MSE.
    """
    return np.divide(
        result.symbols,
        result.decision_gain,
        out=np.zeros_like(result.symbols),
        where=~result.erasures,
    )
