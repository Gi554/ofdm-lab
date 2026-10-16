"""Essais appariés à canal FIR connu, fixe pendant tout le burst OFDM."""

from dataclasses import asdict

import numpy as np

from .channels import apply_multipath, channel_memory, frequency_response, impulse_response
from .configuration import OFDMConfig
from .metrics import mean_binomial_interval
from .noise import _positive_integer, add_awgn
from .ofdm_simulation import energy_budget
from .receiver import receive
from .theory import ber_awgn, ser_awgn
from .transmitter import transmit


def simulate_known_channel(
    config: OFDMConfig,
    taps,
    ebn0_db: float | None,
    n_ofdm_symbols: int,
    seed: int,
    reference: str = "useful",
    confidence: float = 0.95,
) -> list[dict]:
    """Comparer none/ZF/MMSE/MMSE à seuils bruts sur les mêmes données et bruit.

    Eb/N0 est référencé à l'émetteur, sans renormaliser la puissance reçue. None désactive
    le bruit. H est connu sans erreur et constant sur le burst. Les IC sont stratifiés par
    porteuse/bit sur les trames indépendantes ; aucun IC n'est annoncé si le CP est court.
    Les références BER/SER sont conditionnelles à cette réalisation, pas moyennées Rayleigh.
    """
    frames = _positive_integer(n_ofdm_symbols, "Le nombre de trames")
    mean_binomial_interval([0], 1, confidence)
    h = impulse_response(taps)
    H = frequency_response(h, config.n_fft)
    sufficient = config.cp_length >= channel_memory(h)
    budget = energy_budget(config, ebn0_db if ebn0_db is not None else 0, reference)
    n0 = budget["noise_variance"] if ebn0_db is not None else 0.0
    data_seed, noise_seed = np.random.SeedSequence(seed).spawn(2)
    bits = np.random.default_rng(data_seed).integers(
        0, 2, frames * config.bits_per_ofdm_symbol, dtype=np.uint8
    )
    tx = transmit(bits, config)
    full = apply_multipath(tx.waveform, h)
    received = add_awgn(full[: tx.waveform.size], n0, noise_seed)
    active = H[config.active_indices]
    if np.any(abs(active) <= 1e-12):
        raise ValueError(
            "La comparaison inclut ZF : les porteuses actives doivent être inversibles."
        )
    theoretical_ber = theoretical_ser = None
    if sufficient:
        if n0 == 0:
            theoretical_ber = theoretical_ser = 0.0
        else:
            effective = budget["effective_useful_ebn0_db"] + 10 * np.log10(abs(active) ** 2)
            theoretical_ber = float(np.mean([ber_awgn(db, config.order) for db in effective]))
            theoretical_ser = float(np.mean([ser_awgn(db, config.order) for db in effective]))
    rows = []
    for label, method, mode in [
        ("none", "none", "gain_aware"),
        ("zf", "zf", "gain_aware"),
        ("mmse", "mmse", "gain_aware"),
        ("mmse_raw", "mmse", "raw"),
    ]:
        rx = receive(
            received,
            config,
            channel_response=H,
            equalizer=method,
            noise_variance=n0,
            decision_mode=mode,
        )
        errors = (rx.bits != bits).reshape(frames, config.n_active, config.bits_per_symbol)
        bit_counts = errors.sum(axis=0)
        symbol_counts = errors.any(axis=2).sum(axis=0)
        bl = bh = sl = sh = None
        if sufficient:
            bl, bh = mean_binomial_interval(bit_counts.ravel(), frames, confidence)
            sl, sh = mean_binomial_interval(symbol_counts, frames, confidence)
        if label == "none":
            expected_mse = float(np.mean(abs(active - 1) ** 2 + n0))
        elif label == "zf":
            expected_mse = float(np.mean(n0 / abs(active) ** 2))
        else:
            expected_mse = float(np.mean(n0 / (abs(active) ** 2 + n0))) if n0 else 0.0
        rows.append(
            {
                **asdict(config),
                "method": label,
                "ebn0_db": ebn0_db,
                "energy_reference": reference,
                "noise_variance": n0,
                "channel_memory": channel_memory(h),
                "cp_sufficient": sufficient,
                "channel_taps": [[float(z.real), float(z.imag)] for z in h],
                "channel_energy": float(np.sum(abs(h) ** 2)),
                "n_ofdm_symbols": frames,
                "n_symbols": frames * config.n_active,
                "n_bits": int(bits.size),
                "bit_errors": int(errors.sum()),
                "symbol_errors": int(symbol_counts.sum()),
                "errors_by_carrier_bit": bit_counts.tolist(),
                "errors_by_carrier": symbol_counts.tolist(),
                "ber": float(errors.mean()),
                "ser": float(symbol_counts.sum() / (frames * config.n_active)),
                "ber_ci_lower": bl,
                "ber_ci_upper": bh,
                "ser_ci_lower": sl,
                "ser_ci_upper": sh,
                "interval_method": "Clopper-Pearson + Bonferroni par porteuse/bit"
                if sufficient
                else "aucun : ISI",
                "confidence": confidence if sufficient else None,
                "ber_theory_conditional": theoretical_ber if label in ("zf", "mmse") else None,
                "ser_theory_conditional": theoretical_ser if label in ("zf", "mmse") else None,
                "mse": float(
                    np.mean(
                        abs(rx.equalized_symbols - tx.grid[:, config.active_indices].ravel()) ** 2
                    )
                ),
                "mse_theory_conditional": expected_mse if sufficient else None,
                "erasures": int(rx.erasures.sum()),
                "seed": int(seed),
                "numpy_version": np.__version__,
            }
        )
    return rows
