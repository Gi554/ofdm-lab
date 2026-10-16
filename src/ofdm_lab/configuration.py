"""Configuration OFDM validée, allocation symétrique sans DC ni Nyquist."""

from dataclasses import dataclass

import numpy as np

from .noise import _finite_real, _positive_integer
from .theory import _order


def _cp_length(value: int, limit: int) -> int:
    if (
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        or not 0 <= value <= limit
    ):
        raise ValueError("La longueur CP doit être entière, entre 0 et la longueur utile.")
    return int(value)


@dataclass(frozen=True)
class OFDMConfig:
    """FFT paire, porteuses -K/2..-1 puis +1..+K/2 ; modulation 2,4,16,64."""

    n_fft: int = 64
    n_active: int = 52
    cp_length: int = 16
    order: int = 4
    spacing_hz: float = 15000

    def __post_init__(self):
        size = _positive_integer(self.n_fft, "La taille FFT")
        active = _positive_integer(self.n_active, "Les porteuses actives")
        if size < 4 or size % 2 or active % 2 or active > size - 2:
            raise ValueError("FFT paire >=4 et nombre actif pair <=N-2 requis (DC/Nyquist nuls).")
        _cp_length(self.cp_length, size)
        _order(self.order)
        spacing = _finite_real(self.spacing_hz, "L'espacement fréquentiel")
        if spacing <= 0 or not np.isfinite(size * spacing):
            raise ValueError("L'espacement doit être positif, Fs finie.")
        # Canonicaliser aussi les entiers NumPy non signés avant les indices négatifs.
        for name, value in {
            "n_fft": size,
            "n_active": active,
            "cp_length": _cp_length(self.cp_length, size),
            "order": _order(self.order),
            "spacing_hz": spacing,
        }.items():
            object.__setattr__(self, name, value)

    @property
    def active_indices(self):
        half = self.n_active // 2
        return np.concatenate((np.arange(-half, 0), np.arange(1, half + 1))) % self.n_fft

    @property
    def bits_per_symbol(self) -> int:
        return int(self.order).bit_length() - 1

    @property
    def bits_per_ofdm_symbol(self) -> int:
        return self.n_active * self.bits_per_symbol

    @property
    def sample_rate_hz(self) -> float:
        return self.n_fft * self.spacing_hz

    @property
    def cp_energy_factor(self) -> float:
        return 1 + self.cp_length / self.n_fft
