"""Monte-Carlo OFDM/AWGN et bilan énergétique explicite, sans canal à mémoire."""

from dataclasses import asdict

import numpy as np

from .configuration import OFDMConfig
from .metrics import ber_interval, binomial_interval, count_errors
from .noise import _positive_integer, add_awgn, noise_variance
from .receiver import receive
from .theory import ber_awgn, ser_awgn
from .transmitter import transmit


def energy_budget(config: OFDMConfig, ebn0_db: float, reference: str = "useful") -> dict:
    """Es=1 par porteuse ; référence Eb utile ou totale incluant le CP en moyenne."""
    if reference not in ("useful", "total"):
        raise ValueError("La référence énergétique doit être useful ou total.")
    factor = config.cp_energy_factor if reference == "total" else 1.0
    variance = noise_variance(ebn0_db, config.bits_per_symbol) * factor
    effective_db = float(ebn0_db - 10 * np.log10(factor))
    return {
        "energy_reference": reference,
        "noise_variance": variance,
        "effective_useful_ebn0_db": effective_db,
        "expected_useful_energy": float(config.n_active),
        "expected_cp_energy": config.n_active * config.cp_length / config.n_fft,
        "expected_total_energy": config.n_active * config.cp_energy_factor,
        "expected_sample_power": config.n_active / config.n_fft,
        "expected_snr_db": float(10 * np.log10(config.n_active / config.n_fft / variance)),
        "cp_penalty_db": float(10 * np.log10(factor)),
        "payload_rate_bps": config.bits_per_ofdm_symbol
        * config.sample_rate_hz
        / (config.n_fft + config.cp_length),
    }


def simulate_ofdm_awgn(
    config: OFDMConfig,
    ebn0_db: float,
    n_ofdm_symbols: int,
    seed: int,
    reference: str = "useful",
    batch_frames: int = 128,
    confidence: float = 0.95,
) -> dict:
    """Effectif de trames fixé ; FFT unitaire, retrait CP et synchronisation parfaite."""
    frames = _positive_integer(n_ofdm_symbols, "Le nombre de symboles OFDM")
    block = _positive_integer(batch_frames, "La taille de bloc")
    binomial_interval(0, 1, confidence)
    budget = energy_budget(config, ebn0_db, reference)
    bits_seed, noise_seed = np.random.SeedSequence(seed).spawn(2)
    rng = np.random.default_rng(bits_seed)
    seeds = noise_seed.spawn((frames + block - 1) // block)
    positions = np.zeros(config.bits_per_symbol, dtype=np.int64)
    errors = symbol_errors = 0
    for index, start in enumerate(range(0, frames, block)):
        count = min(block, frames - start)
        bits = rng.integers(0, 2, count * config.bits_per_ofdm_symbol, dtype=np.uint8)
        tx = transmit(bits, config)
        rx = receive(add_awgn(tx.waveform, budget["noise_variance"], seeds[index]), config)
        counts = count_errors(bits, rx.bits, config.bits_per_symbol)
        errors += counts.bit_errors
        symbol_errors += counts.symbol_errors
        positions += counts.per_bit_position
    n_symbols = frames * config.n_active
    n_bits = n_symbols * config.bits_per_symbol
    bl, bh = ber_interval(positions, n_symbols, confidence)
    sl, sh = binomial_interval(symbol_errors, n_symbols, confidence)
    return {
        **asdict(config),
        **budget,
        "ebn0_db": float(ebn0_db),
        "n_ofdm_symbols": frames,
        "n_symbols": n_symbols,
        "n_bits": n_bits,
        "bit_errors": errors,
        "symbol_errors": symbol_errors,
        "errors_per_bit_position": positions.tolist(),
        "ber": errors / n_bits,
        "ser": symbol_errors / n_symbols,
        "ber_ci_lower": bl,
        "ber_ci_upper": bh,
        "ser_ci_lower": sl,
        "ser_ci_upper": sh,
        "ber_theory_exact": ber_awgn(budget["effective_useful_ebn0_db"], config.order),
        "ser_theory_exact": ser_awgn(budget["effective_useful_ebn0_db"], config.order),
        "confidence": confidence,
        "seed": int(seed),
        "batch_frames": block,
        "numpy_version": np.__version__,
    }
