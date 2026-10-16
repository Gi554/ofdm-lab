"""Émetteur OFDM : mapping existant, allocation, IFFT unitaire puis CP."""

from dataclasses import dataclass

import numpy as np

from .bits import validate_bits
from .configuration import OFDMConfig, _cp_length
from .modulation import modulate_bpsk, modulate_qam, modulate_qpsk
from .theory import _order
from .transforms import _finite_array, ifft


def add_cyclic_prefix(samples, cp_length: int):
    """Copier la fin du dernier axe ; CP nul géré sans duplication accidentelle."""
    values = _finite_array(samples)
    cp = _cp_length(cp_length, values.shape[-1])
    return np.concatenate((values[..., -cp:], values), axis=-1) if cp else values.copy()


@dataclass(frozen=True)
class OFDMTransmission:
    """Grille native, signal utile, symboles avec CP et flux sérialisé."""

    grid: np.ndarray
    useful: np.ndarray
    with_cp: np.ndarray
    waveform: np.ndarray


def transmit(bits, config: OFDMConfig) -> OFDMTransmission:
    """Transmettre des blocs complets ; aucun bourrage ou métadonnée implicite."""
    values = validate_bits(bits)
    if values.size == 0 or values.size % config.bits_per_ofdm_symbol:
        raise ValueError("Les bits doivent remplir un nombre entier non nul de symboles OFDM.")
    mapped = map_bits(values, config.order)
    grid = np.zeros((values.size // config.bits_per_ofdm_symbol, config.n_fft), dtype=complex)
    grid[:, config.active_indices] = mapped.reshape(-1, config.n_active)
    useful = ifft(grid)
    with_cp = add_cyclic_prefix(useful, config.cp_length)
    return OFDMTransmission(grid, useful, with_cp, with_cp.reshape(-1))


def map_bits(bits, order: int):
    """Sélectionner le mapping existant, sans changer sa normalisation Es=1."""
    order = _order(order)
    if order == 2:
        return modulate_bpsk(bits)
    if order == 4:
        return modulate_qpsk(bits)
    return modulate_qam(bits, order)
