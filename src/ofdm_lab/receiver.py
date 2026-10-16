"""Récepteur à début connu : retrait CP, FFT et égalisation diagonale optionnelle."""

from dataclasses import dataclass

import numpy as np

from .configuration import OFDMConfig, _cp_length
from .demodulation import demodulate_bpsk, demodulate_qam, demodulate_qpsk
from .equalization import decision_symbols, equalize
from .transforms import _finite_array, fft


def remove_cyclic_prefix(samples, cp_length: int):
    """Retirer le CP sur le dernier axe ; imposer CP <= longueur utile restante."""
    values = _finite_array(samples)
    cp = _cp_length(cp_length, values.shape[-1] // 2)
    return values[..., cp:].copy()


@dataclass(frozen=True)
class OFDMReception:
    """Bits décidés et symboles fréquentiels avant décision, en ordre d'allocation."""

    bits: np.ndarray
    symbols: np.ndarray
    grid: np.ndarray
    equalized_symbols: np.ndarray | None = None
    decision_gain: np.ndarray | None = None
    erasures: np.ndarray | None = None


def receive(
    waveform,
    config: OFDMConfig,
    *,
    channel_response=None,
    equalizer="none",
    noise_variance=0.0,
    decision_mode="gain_aware",
) -> OFDMReception:
    """Début connu ; égalisation optionnelle avec H natif connu, constant ou par trame.

    symbols conserve les observations brutes ; equalized_symbols contient l'estimation.
    gain_aware utilise G pour les décisions MMSE. raw laisse les seuils de l'alphabet
    initial et expose volontairement le biais. Le CP doit couvrir la mémoire pour Y=HX+W.
    """
    values = _finite_array(waveform)
    width = config.n_fft + config.cp_length
    if values.ndim != 1 or values.size % width:
        raise ValueError("Le flux reçu doit être 1D et contenir des symboles OFDM complets.")
    grid = fft(remove_cyclic_prefix(values.reshape(-1, width), config.cp_length))
    raw = grid[:, config.active_indices]
    if decision_mode not in ("gain_aware", "raw"):
        raise ValueError("decision_mode doit être gain_aware ou raw.")
    if equalizer == "none":
        estimates = raw
        decision = raw
        gain = np.ones(raw.shape)
        erasures = np.zeros(raw.shape, dtype=bool)
    else:
        if channel_response is None:
            raise ValueError("La réponse H connue est requise pour égaliser.")
        h = np.asarray(channel_response, dtype=complex)
        if h.ndim not in (1, 2) or h.shape[-1] != config.n_fft or not np.all(np.isfinite(h)):
            raise ValueError("H doit avoir N cases natives, éventuellement une ligne par trame.")
        try:
            h = np.broadcast_to(h, grid.shape)
        except ValueError as error:
            raise ValueError("Le nombre de trames de H est incompatible.") from error
        result = equalize(raw, h[:, config.active_indices], equalizer, noise_variance)
        estimates = result.symbols
        gain = result.decision_gain
        erasures = result.erasures
        decision = decision_symbols(result) if decision_mode == "gain_aware" else estimates
    symbols = raw.reshape(-1)
    decided = decision.reshape(-1)
    if config.order == 2:
        bits = demodulate_bpsk(decided)
    elif config.order == 4:
        bits = demodulate_qpsk(decided)
    else:
        bits = demodulate_qam(decided, config.order)
    return OFDMReception(
        bits, symbols, grid, estimates.reshape(-1), gain.reshape(-1), erasures.reshape(-1)
    )
