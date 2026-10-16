"""Pilotes en peigne, LS par trame et interpolation complexe séparée par bande."""

from dataclasses import dataclass

import numpy as np

from .bits import validate_bits
from .configuration import OFDMConfig
from .noise import _finite_real, _positive_integer
from .receiver import receive
from .transforms import _finite_array, ifft
from .transmitter import OFDMTransmission, add_cyclic_prefix, map_bits


@dataclass(frozen=True)
class PilotLayout:
    """Pilotes aux extrémités de chaque demi-bande active ; pas d'extrapolation.

    spacing est le pas maximal en indices de porteuses. DC n'est jamais traversée
    par l'interpolation. Les pilotes ont Es=1, phases QPSK déterministes publiques.
    """

    config: OFDMConfig
    spacing: int = 4

    def __post_init__(self):
        object.__setattr__(self, "spacing", _positive_integer(self.spacing, "Le pas pilote"))
        if not self.data_positions.size:
            raise ValueError("Le plan pilote doit laisser au moins une porteuse de données.")

    @property
    def pilot_positions(self):
        half = self.config.n_active // 2
        side = np.unique(np.r_[np.arange(0, half, self.spacing), half - 1])
        return np.r_[side, side + half]

    @property
    def data_positions(self):
        return np.setdiff1d(np.arange(self.config.n_active), self.pilot_positions)

    @property
    def pilot_symbols(self):
        # Valeurs exactes, sans petit résidu dû aux fonctions trigonométriques.
        return np.array([1, 1j, -1, -1j])[np.arange(self.pilot_positions.size) % 4]

    @property
    def bits_per_frame(self):
        return int(self.data_positions.size * self.config.bits_per_symbol)


def transmit_pilots(bits, layout: PilotLayout) -> OFDMTransmission:
    """Mapper uniquement les bits utiles ; pilotes publics insérés, aucun padding."""
    values = validate_bits(bits)
    if values.size == 0 or values.size % layout.bits_per_frame:
        raise ValueError("Les bits doivent remplir des trames de données complètes.")
    config = layout.config
    grid = np.zeros((values.size // layout.bits_per_frame, config.n_fft), dtype=complex)
    active = config.active_indices
    grid[:, active[layout.data_positions]] = map_bits(values, config.order).reshape(
        -1, layout.data_positions.size
    )
    grid[:, active[layout.pilot_positions]] = layout.pilot_symbols
    useful = ifft(grid)
    blocks = add_cyclic_prefix(useful, config.cp_length)
    return OFDMTransmission(grid, useful, blocks, blocks.ravel())


def interpolation_matrix(layout: PilotLayout):
    """A réel : H_hat_active = H_hat_pilotes @ A.T ; deux demi-bandes indépendantes."""
    positions = layout.pilot_positions
    identity = np.eye(positions.size)
    weights = np.zeros((layout.config.n_active, positions.size))
    half = layout.config.n_active // 2
    for start in [0, half]:
        mask = (positions >= start) & (positions < start + half)
        for column in np.flatnonzero(mask):
            weights[start : start + half, column] = np.interp(
                np.arange(start, start + half), positions[mask], identity[mask, column]
            )
    return weights


def estimate_channel_ls(grid, layout: PilotLayout):
    """Yp/Xp par trame puis interpolation linéaire réel/imag ; gardes H_hat=0.

    Les zéros sur les gardes signifient non estimé. Aucun lissage temporel, aucune
    mémoire vraie ni réponse H vraie n'est utilisée par l'estimateur.
    """
    values = _finite_array(grid)
    if values.ndim != 2 or values.shape[1] != layout.config.n_fft:
        raise ValueError("La grille reçue doit avoir une ligne par trame et N colonnes.")
    pilots = values[:, layout.config.active_indices[layout.pilot_positions]] / layout.pilot_symbols
    result = np.zeros(values.shape, dtype=complex)
    result[:, layout.config.active_indices] = pilots @ interpolation_matrix(layout).T
    return result


def pilot_energy_budget(layout: PilotLayout, ebn0_db: float, reference="total"):
    """Eb par bit de données : total inclut pilotes et CP ; data exclut les deux.

    Pilotes déterministes : leur énergie CP est calculée exactement ; pour les
    données indépendantes de moyenne nulle Es=1, Ecp_data=Kd*C/N. Ne pas supposer
    automatiquement Ecp=(Kd+Kp)*C/N pour des pilotes cohérents déterministes.
    """
    if reference not in ("data", "total"):
        raise ValueError("Référence attendue : data ou total.")
    db = _finite_real(ebn0_db, "Eb/N0")
    config = layout.config
    kd = int(layout.data_positions.size)
    grid = np.zeros(config.n_fft, dtype=complex)
    grid[config.active_indices[layout.pilot_positions]] = layout.pilot_symbols
    pilot_wave = ifft(grid)
    pilot_cp = float(np.sum(abs(pilot_wave[-config.cp_length :]) ** 2)) if config.cp_length else 0.0
    useful = float(config.n_active)
    cp = kd * config.cp_length / config.n_fft + pilot_cp
    eb_total = (useful + cp) / layout.bits_per_frame
    eb = eb_total if reference == "total" else 1 / config.bits_per_symbol
    with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
        variance = eb * 10.0 ** (-db / 10)
    if not np.isfinite(variance) or variance <= 0:
        raise ValueError("La variance de bruit doit être finie et strictement positive.")
    return dict(
        energy_reference=reference,
        noise_variance=float(variance),
        expected_useful_energy=useful,
        expected_cp_energy=float(cp),
        deterministic_pilot_cp_energy=pilot_cp,
        expected_total_energy=float(useful + cp),
        eb_total_per_data_bit=float(eb_total),
        n_data=kd,
        n_pilots=int(layout.pilot_positions.size),
        payload_rate_bps=layout.bits_per_frame
        * config.sample_rate_hz
        / (config.n_fft + config.cp_length),
        overhead_factor=float(eb_total * config.bits_per_symbol),
    )


def receive_pilots(
    waveform, layout: PilotLayout, *, channel_response=None, equalizer="none", noise_variance=0.0
):
    """Réutiliser le récepteur OFDM ; exclure les pilotes des bits décidés et du BER.

    L'estimation est explicite : appeler estimate_channel_ls sur la grille reçue,
    puis fournir H_hat comme channel_response. Les creux ZF sont refusés sans epsilon caché.
    """
    rx = receive(
        waveform,
        layout.config,
        channel_response=channel_response,
        equalizer=equalizer,
        noise_variance=noise_variance,
    )
    return rx.bits.reshape(-1, layout.config.n_active, layout.config.bits_per_symbol)[
        :, layout.data_positions, :
    ].ravel()
