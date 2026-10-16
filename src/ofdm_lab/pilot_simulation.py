"""Essais appariés : pilotes LS interpolés, H parfait et absence de correction."""

import numpy as np

from .channels import apply_multipath, channel_memory, frequency_response, impulse_response
from .estimation import (
    PilotLayout,
    estimate_channel_ls,
    interpolation_matrix,
    pilot_energy_budget,
    receive_pilots,
    transmit_pilots,
)
from .metrics import mean_binomial_interval
from .noise import _positive_integer, add_awgn
from .receiver import receive


def simulate_pilot_channel(
    layout: PilotLayout, taps, ebn0_db: float, n_ofdm_symbols: int, seed: int, reference="total"
):
    """CP suffisant, timing parfait, CFO nul ; estimation indépendante par trame.

    Même burst pour les trois décisions, BER seulement sur les données. Les IC
    stratifiés restent valides malgré la corrélation entre porteuses d'une trame,
    car aucune moyenne temporelle ni estimation partagée entre trames n'est utilisée.
    """
    frames = _positive_integer(n_ofdm_symbols, "Le nombre de trames")
    config = layout.config
    h = impulse_response(taps)
    if config.cp_length < channel_memory(h):
        raise ValueError("Cette expérience d'estimation requiert un CP suffisant.")
    truth = frequency_response(h, config.n_fft)
    budget = pilot_energy_budget(layout, ebn0_db, reference)
    n0 = budget["noise_variance"]
    data_seed, noise_seed = np.random.SeedSequence(seed).spawn(2)
    bits = np.random.default_rng(data_seed).integers(
        0, 2, frames * layout.bits_per_frame, dtype=np.uint8
    )
    tx = transmit_pilots(bits, layout)
    received = add_awgn(apply_multipath(tx.waveform, h)[: tx.waveform.size], n0, noise_seed)
    estimated = estimate_channel_ls(receive(received, config).grid, layout)
    indices = config.active_indices[layout.data_positions]
    pilot_indices = config.active_indices[layout.pilot_positions]
    a = interpolation_matrix(layout)[layout.data_positions]
    covariance = a @ a.T
    bias = a @ truth[pilot_indices] - truth[indices]
    d = indices.size
    expected_mse = float(np.mean(abs(bias) ** 2) + n0 * np.trace(covariance) / d)
    mse_variance = float(
        (n0**2 * np.sum(covariance**2) + 2 * n0 * np.real(np.vdot(bias, covariance @ bias)))
        / d**2
        / frames
    )
    rows = []
    for method, response in [("none", None), ("perfect", truth), ("pilot_linear", estimated)]:
        decided = receive_pilots(
            received,
            layout,
            channel_response=response,
            equalizer="none" if response is None else "zf",
        )
        errors = (decided != bits).reshape(frames, d, config.bits_per_symbol)
        counts = errors.sum(axis=0)
        lower, upper = mean_binomial_interval(counts.ravel(), frames, 0.95)
        model = np.ones(config.n_fft) if response is None else response
        mse = float(np.mean(abs(model[..., indices] - truth[indices]) ** 2))
        rows.append(
            dict(
                **budget,
                method=method,
                order=config.order,
                n_fft=config.n_fft,
                n_active=config.n_active,
                cp_length=config.cp_length,
                pilot_spacing=layout.spacing,
                pilot_positions=layout.pilot_positions.tolist(),
                pilot_symbols=[[float(z.real), float(z.imag)] for z in layout.pilot_symbols],
                channel_taps=[[float(z.real), float(z.imag)] for z in h],
                channel_memory=channel_memory(h),
                ebn0_db=float(ebn0_db),
                n_ofdm_symbols=frames,
                n_bits=int(bits.size),
                bit_errors=int(errors.sum()),
                errors_by_carrier_bit=counts.tolist(),
                equalizer="none" if response is None else "zf",
                ber=float(errors.mean()),
                ber_ci_lower=lower,
                ber_ci_upper=upper,
                confidence=0.95,
                interval_method="Clopper-Pearson + Bonferroni par porteuse/bit",
                channel_mse_data=mse,
                channel_mse_theory=expected_mse if method == "pilot_linear" else mse,
                channel_mse_mean_variance=mse_variance if method == "pilot_linear" else 0.0,
                interpolation_bias_mse=float(np.mean(abs(bias) ** 2)),
                pilot_ls_mse=float(
                    np.mean(abs(estimated[:, pilot_indices] - truth[pilot_indices]) ** 2)
                ),
                pilot_ls_mse_theory=float(n0),
                seed=int(seed),
                numpy_version=np.__version__,
            )
        )
    return rows
