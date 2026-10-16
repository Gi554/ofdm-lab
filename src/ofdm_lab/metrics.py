"""Compteurs d'erreurs et intervalles fréquentistes pour essais indépendants."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike
from scipy.stats import beta

from .bits import validate_bits
from .noise import _finite_real, _positive_integer


@dataclass(frozen=True)
class ErrorCounts:
    """Résultat immuable de la comparaison de deux vecteurs binaires non vides."""

    n_bits: int
    n_symbols: int
    bit_errors: int
    symbol_errors: int
    per_bit_position: tuple[int, ...]

    @property
    def ber(self) -> float:
        return self.bit_errors / self.n_bits

    @property
    def ser(self) -> float:
        return self.symbol_errors / self.n_symbols


def count_errors(transmitted: ArrayLike, received: ArrayLike, bits_per_symbol: int) -> ErrorCounts:
    """Compter les erreurs ; un symbole est erroné si au moins un de ses bits diffère."""
    k = _positive_integer(bits_per_symbol, "Le nombre de bits par symbole")
    tx, rx = validate_bits(transmitted), validate_bits(received)
    if tx.size == 0 or tx.shape != rx.shape or tx.size % k:
        raise ValueError("Les séquences doivent être non vides, de même taille et multiples de k.")
    errors = (tx != rx).reshape(-1, k)
    return ErrorCounts(
        int(tx.size),
        int(errors.shape[0]),
        int(errors.sum()),
        int(np.count_nonzero(np.any(errors, axis=1))),
        tuple(int(n) for n in errors.sum(axis=0)),
    )


def _confidence(value: float) -> float:
    result = _finite_real(value, "Le niveau de confiance")
    if not 0 < result < 1:
        raise ValueError("Le niveau de confiance doit être strictement entre 0 et 1.")
    return result


def _error_count(errors: int, trials: int) -> int:
    if isinstance(errors, (bool, np.bool_)) or not isinstance(errors, (int, np.integer)):
        raise ValueError("Le nombre d'erreurs doit être un entier entre 0 et N.")
    if not 0 <= errors <= trials:
        raise ValueError("Le nombre d'erreurs doit être un entier entre 0 et N.")
    return int(errors)


def _clopper_pearson(errors: int, trials: int, alpha: float) -> tuple[float, float]:
    lower = 0.0 if errors == 0 else float(beta.ppf(alpha / 2, errors, trials - errors + 1))
    upper = 1.0 if errors == trials else float(beta.isf(alpha / 2, errors + 1, trials - errors))
    return lower, upper


def binomial_interval(errors: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Intervalle bilatéral exact Clopper–Pearson, N fixé avant observation.

    Les essais doivent être Bernoulli indépendants et de même probabilité. La couverture
    est au moins confidence ; un arrêt en fonction des erreurs invalide cette garantie.
    """
    n = _positive_integer(trials, "Le nombre d'essais")
    e = _error_count(errors, n)
    return _clopper_pearson(e, n, 1 - _confidence(confidence))


def ber_interval(
    per_bit_position: ArrayLike, n_symbols: int, confidence: float = 0.95
) -> tuple[float, float]:
    """IC BER conservateur : Clopper–Pearson par position + correction Bonferroni.

    Chaque position est observée sur n_symbols symboles indépendants. Les erreurs des
    positions d'un même symbole peuvent être corrélées (QAM). La moyenne des bornes
    simultanées couvre la moyenne des probabilités avec une confiance au moins donnée.
    """
    n = _positive_integer(n_symbols, "Le nombre de symboles")
    counts = np.asarray(per_bit_position)
    if counts.ndim != 1 or counts.size == 0:
        raise ValueError("Il faut un compteur par position binaire dans le symbole.")
    values = [_error_count(e, n) for e in counts]
    alpha = (1 - _confidence(confidence)) / len(values)
    intervals = np.array([_clopper_pearson(e, n, alpha) for e in values])
    return float(intervals[:, 0].mean()), float(intervals[:, 1].mean())


def zero_error_upper_bound(trials: int, confidence: float = 0.95) -> float:
    """Borne unilatérale après zéro erreur sur N essais Bernoulli indépendants fixes."""
    n = _positive_integer(trials, "Le nombre d'essais")
    return float(-np.expm1(np.log1p(-_confidence(confidence)) / n))
