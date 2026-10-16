"""AWGN complexe circulaire et conversions scalaires de rapports énergétiques.

Convention : Es = énergie moyenne de l'alphabet, k = bits par symbole,
E|n|² = N0 et Var(Re(n)) = Var(Im(n)) = N0/2. Aucun CP ni pilote à ce stade.
"""

from numbers import Real

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _finite_real(value: float, name: str) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(f"{name} doit être un nombre réel fini.")
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f"{name} doit être un nombre réel fini.")
    return result


def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} doit être un entier strictement positif.")
    if value <= 0:
        raise ValueError(f"{name} doit être un entier strictement positif.")
    return int(value)


def db_to_linear(value_db: float) -> float:
    """Convertir un rapport de puissances/énergies en dB en rapport linéaire."""
    value = _finite_real(value_db, "Le rapport en dB")
    with np.errstate(over="ignore", under="ignore"):
        result = float(np.power(10.0, value / 10.0))
    if not np.isfinite(result) or result <= 0:
        raise ValueError("Le rapport en dB dépasse la plage numérique représentable.")
    return result


def ebn0_to_esn0_db(ebn0_db: float, bits_per_symbol: int) -> float:
    """Es/N0 [dB] = Eb/N0 [dB] + 10 log10(k), sans codage ni surcoût."""
    k = _positive_integer(bits_per_symbol, "Le nombre de bits par symbole")
    return _finite_real(ebn0_db, "Eb/N0") + 10.0 * np.log10(k)


def esn0_to_snr_db(esn0_db: float, samples_per_symbol: int = 1) -> float:
    """SNR [dB] = Es/N0 [dB] - 10 log10(L), sous convention d'énergie discrète.

    L est le nombre d'échantillons par symbole. Cette conversion suppose une mise
    en forme conservant Es=sum|x[n]|² par symbole et E|n[n]|²=N0 par échantillon.
    Elle n'est pas une formule générale pour un signal OFDM avec CP et pilotes.
    """
    count = _positive_integer(samples_per_symbol, "Les échantillons par symbole")
    return _finite_real(esn0_db, "Es/N0") - 10.0 * np.log10(count)


def noise_variance(ebn0_db: float, bits_per_symbol: int, symbol_energy: float = 1.0) -> float:
    """Calculer N0 = Es / (k * Eb/N0_lin), pour des échantillons aux instants symbole.

    Es est la moyenne de l'alphabet, jamais une normalisation mesurée du tirage
    ou du signal reçu. Le retour est la variance complexe totale, pas celle d'un axe.
    """
    k = _positive_integer(bits_per_symbol, "Le nombre de bits par symbole")
    energy = _finite_real(symbol_energy, "Es")
    if energy <= 0:
        raise ValueError("Es doit être strictement positive.")
    result = (energy / k) / db_to_linear(ebn0_db)
    if not np.isfinite(result) or result <= 0:
        raise ValueError("La variance de bruit dépasse la plage numérique représentable.")
    return result


def add_awgn(
    signal: ArrayLike, variance: float, seed: int | np.random.SeedSequence | None = None
) -> NDArray[np.complex128]:
    """Ajouter n ~ CN(0, variance) à un vecteur 1D, via un générateur local.

    Une variance nulle renvoie une copie complexe du signal, sans bruit.
    Le signal d'entrée n'est jamais modifié. seed fixe la reproductibilité.
    """
    values = np.asarray(signal, dtype=np.complex128)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("Le signal doit être un vecteur complexe fini.")
    power = _finite_real(variance, "La variance complexe")
    if power < 0:
        raise ValueError("La variance doit être positive ou nulle.")
    rng = np.random.default_rng(seed)
    scale = np.sqrt(power / 2.0)
    noise = scale * (rng.standard_normal(values.size) + 1j * rng.standard_normal(values.size))
    return values + noise
