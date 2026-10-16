"""Récepteur idéal : début connu, retrait CP, FFT unitaire et décisions cohérentes."""

from dataclasses import dataclass

import numpy as np

from .configuration import OFDMConfig, _cp_length
from .demodulation import demodulate_bpsk, demodulate_qam, demodulate_qpsk
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


def receive(waveform, config: OFDMConfig) -> OFDMReception:
    """Canal idéal/AWGN seulement : ni égalisation ni recherche de synchronisation."""
    values = _finite_array(waveform)
    width = config.n_fft + config.cp_length
    if values.ndim != 1 or values.size % width:
        raise ValueError("Le flux reçu doit être 1D et contenir des symboles OFDM complets.")
    grid = fft(remove_cyclic_prefix(values.reshape(-1, width), config.cp_length))
    symbols = grid[:, config.active_indices].reshape(-1)
    if config.order == 2:
        bits = demodulate_bpsk(symbols)
    elif config.order == 4:
        bits = demodulate_qpsk(symbols)
    else:
        bits = demodulate_qam(symbols, config.order)
    return OFDMReception(bits, symbols, grid)
