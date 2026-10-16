"""CFO normalisé par l'espacement des porteuses, début de burst connu."""

from dataclasses import dataclass

import numpy as np

from .configuration import OFDMConfig, _cp_length
from .noise import _finite_real, _positive_integer
from .transforms import _finite_array


@dataclass(frozen=True)
class CFOEstimate:
    """Estimation modulo une porteuse ; cohérence diagnostique entre 0 et 1."""

    normalized_offset: float
    correlation: complex
    coherence: float
    n_pairs: int


def apply_frequency_offset(waveform, normalized_offset: float, n_fft: int, *, start_sample=0):
    """Appliquer exp(+j2π epsilon n/N) sur le flux 1D, CP compris.

    epsilon=delta_f/spacing_hz. start_sample permet de traiter des morceaux sans
    réinitialiser la phase ; une correction utilise -epsilon avec la même origine.
    """
    values = _finite_array(waveform)
    if values.ndim != 1:
        raise ValueError("Le flux CFO doit être 1D.")
    size = _positive_integer(n_fft, "La taille FFT")
    offset = _finite_real(normalized_offset, "Le CFO normalisé")
    if (
        isinstance(start_sample, (bool, np.bool_))
        or not isinstance(start_sample, (int, np.integer))
        or start_sample < 0
    ):
        raise ValueError("L'origine doit être un entier non négatif.")
    with np.errstate(over="ignore", invalid="ignore"):
        phase = 2 * np.pi * offset * (int(start_sample) + np.arange(values.size)) / size
    if not np.all(np.isfinite(phase)):
        raise ValueError("La phase dépasse la plage numérique représentable.")
    return values * np.exp(1j * phase)


def estimate_cfo_cp(waveform, config: OFDMConfig, *, channel_memory=0) -> CFOEstimate:
    """Corréler conj(r[n]) r[n+N] sur le CP non contaminé par le symbole précédent.

    Début exact connu, CFO constant sur le burst. Écarter les premiers memory
    échantillons du CP nécessite une borne connue de la mémoire FIR. CP>memory
    requis : CP=memory suffit à diagonaliser, mais ne laisse aucune paire exploitable.
    La phase principale ne fournit que epsilon modulo 1, dans [-0.5,0.5].
    """
    values = _finite_array(waveform)
    width = config.n_fft + config.cp_length
    memory = _cp_length(channel_memory, config.n_fft)
    if values.ndim != 1 or values.size % width:
        raise ValueError("Un burst 1D avec trames complètes est requis.")
    if config.cp_length <= memory:
        raise ValueError("Le CP doit dépasser la mémoire pour fournir des paires valides.")
    blocks = values.reshape(-1, width)
    first = blocks[:, memory : config.cp_length]
    second = blocks[:, config.n_fft + memory : config.n_fft + config.cp_length]
    # Mise à l'échelle commune : protège la corrélation sans changer sa phase.
    scale = max(float(np.max(abs(first))), float(np.max(abs(second))))
    if scale == 0:
        raise ValueError("Aucune énergie dans les paires CP.")
    a, b = first / scale, second / scale
    correlation = np.vdot(a, b)
    energy = np.linalg.norm(a) * np.linalg.norm(b)
    if energy == 0 or abs(correlation) <= np.finfo(float).eps * energy:
        raise ValueError("La corrélation CP ne permet pas une estimation de phase.")
    return CFOEstimate(
        float(np.angle(correlation) / (2 * np.pi)),
        complex(correlation),
        float(min(1, abs(correlation) / energy)),
        int(first.size),
    )


def cfo_tone_response(normalized_offset: float, n_fft: int):
    """Réponse FFT unitaire d'une porteuse DC unitaire après CFO, longueur N.

    Somme des puissances=1 ; |C[0]|² est la fraction restée sur la porteuse initiale.
    Les N-1 autres cases mesurent la fuite spectrale totale, gardes comprises.
    """
    size = _positive_integer(n_fft, "La taille FFT")
    samples = np.ones(size, dtype=complex) / np.sqrt(size)
    return np.fft.fft(apply_frequency_offset(samples, normalized_offset, size), norm="ortho")
