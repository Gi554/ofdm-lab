"""Canaux FIR causaux en bande de base et évanouissement Rayleigh statique."""

import numpy as np
from numpy.typing import ArrayLike

from .noise import _positive_integer
from .transforms import _finite_array


def impulse_response(taps: ArrayLike) -> np.ndarray:
    """Valider une réponse 1D finie et non nulle ; aucune normalisation implicite."""
    values = _finite_array(taps)
    if values.ndim != 1 or not np.any(values != 0):
        raise ValueError("Le canal doit être un vecteur fini non nul.")
    return values.copy()


def channel_memory(taps: ArrayLike) -> int:
    """Dernier retard non nul [échantillons], en ignorant les zéros terminaux."""
    values = impulse_response(taps)
    return int(np.flatnonzero(values != 0)[-1])


def apply_multipath(signal: ArrayLike, taps: ArrayLike) -> np.ndarray:
    """Convolution linéaire complète, état initial nul, queue de canal conservée.

    Le résultat a Nx+Lh-1 échantillons. Ne pas traiter séparément chaque bloc OFDM :
    cela supprimerait artificiellement l'interférence entre symboles.
    """
    values = _finite_array(signal)
    if values.ndim != 1:
        raise ValueError("Le flux doit être un vecteur 1D non vide.")
    return np.convolve(values, impulse_response(taps), mode="full")


def frequency_response(taps: ArrayLike, n_fft: int) -> np.ndarray:
    """H[k]=sum_l h[l] exp(-j2πkl/N), FFT NON normalisée, en ordre natif.

    Ainsi FFT_unitaire(h*x)=H*FFT_unitaire(x) si la convolution est circulaire.
    Aucun coefficient ne peut être tronqué silencieusement.
    """
    values = impulse_response(taps)
    size = _positive_integer(n_fft, "La taille FFT")
    if values.size > size:
        raise ValueError("La réponse impulsionnelle ne doit pas dépasser la taille FFT.")
    return np.fft.fft(values, n=size)


def rayleigh_channel(delays: ArrayLike, powers: ArrayLike, seed: int | None = None) -> np.ndarray:
    """Tirer un canal statique : h[d_l] ~ CN(0,p_l/somme(p)), trajets indépendants.

    Les retards sont uniques, entiers et >=0, en échantillons. Les puissances sont
    réelles, finies, >=0 et de somme positive. E somme|h|²=1, sans normaliser le tirage.
    Ce modèle n'inclut ni Doppler ni variation pendant une transmission.
    """
    d = np.asarray(delays)
    p = np.asarray(powers)
    if d.ndim != 1 or d.size == 0 or d.dtype.kind not in "iu" or np.any(d < 0):
        raise ValueError("Les retards doivent être des entiers non négatifs distincts.")
    indices = np.array([int(value) for value in d], dtype=np.int64)
    if np.unique(indices).size != indices.size:
        raise ValueError("Les retards doivent être distincts.")
    if p.ndim != 1 or p.shape != d.shape or p.dtype.kind not in "iuf":
        raise ValueError("Un profil de puissances réelles est requis pour chaque trajet.")
    p = p.astype(float)
    if not np.all(np.isfinite(p)) or np.any(p < 0) or not np.isfinite(p.sum()) or p.sum() <= 0:
        raise ValueError("Les puissances doivent être finies, non négatives et de somme positive.")
    rng = np.random.default_rng(seed)
    gains = np.sqrt(p / p.sum() / 2) * (
        rng.standard_normal(d.size) + 1j * rng.standard_normal(d.size)
    )
    response = np.zeros(int(indices.max()) + 1, dtype=complex)
    response[indices] = gains
    return response
