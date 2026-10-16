"""Monte-Carlo AWGN par blocs, effectif fixé a priori, données et bruit indépendants."""

import numpy as np

from .demodulation import demodulate_bpsk, demodulate_qam, demodulate_qpsk
from .metrics import ber_interval, binomial_interval, count_errors, zero_error_upper_bound
from .modulation import modulate_bpsk, modulate_qam, modulate_qpsk
from .noise import _positive_integer, add_awgn, ebn0_to_esn0_db, noise_variance
from .theory import _order, ber_awgn, qam_ber_nearest_neighbor, ser_awgn


def simulate_awgn(
    order: int,
    ebn0_db: float,
    n_bits: int,
    seed: int,
    batch_symbols: int = 20000,
    confidence: float = 0.95,
) -> dict:
    """Simuler un point BER/SER sur exactement n_bits bits, sans arrêt sur erreurs.

    L'effectif, la graine et la taille de blocs sont nécessaires à la reproductibilité.
    Les intervalles BER tiennent compte de la dépendance entre bits d'un symbole QAM.
    Aucun CP, pilote, codage ni suréchantillonnage. Es=1, phase et timing parfaits.
    """
    m = _order(order)
    k = m.bit_length() - 1
    count = _positive_integer(n_bits, "Le nombre de bits")
    block = _positive_integer(batch_symbols, "La taille de bloc en symboles")
    if count % k:
        raise ValueError("Le nombre de bits doit être un multiple de log2(M).")
    # Valider la confiance avant de lancer un calcul potentiellement long.
    binomial_interval(0, 1, confidence)
    variance = noise_variance(ebn0_db, k)
    data_sequence, noise_sequence = np.random.SeedSequence(seed).spawn(2)
    data_rng = np.random.default_rng(data_sequence)
    symbol_count = count // k
    noise_seeds = noise_sequence.spawn((symbol_count + block - 1) // block)
    if m == 2:
        mod, demod = modulate_bpsk, demodulate_bpsk
    elif m == 4:
        mod, demod = modulate_qpsk, demodulate_qpsk
    else:
        mod, demod = lambda b: modulate_qam(b, m), lambda y: demodulate_qam(y, m)
    positions = np.zeros(k, dtype=np.int64)
    errors, symbol_errors = 0, 0
    for index, start in enumerate(range(0, symbol_count, block)):
        size = min(block, symbol_count - start)
        bits = data_rng.integers(0, 2, size=size * k, dtype=np.uint8)
        recovered = demod(add_awgn(mod(bits), variance, noise_seeds[index]))
        counts = count_errors(bits, recovered, k)
        positions += np.asarray(counts.per_bit_position)
        errors += counts.bit_errors
        symbol_errors += counts.symbol_errors
    ber_low, ber_high = ber_interval(positions, symbol_count, confidence)
    ser_low, ser_high = binomial_interval(symbol_errors, symbol_count, confidence)
    return {
        "order": m,
        "modulation": {2: "BPSK", 4: "QPSK", 16: "16-QAM", 64: "64-QAM"}[m],
        "ebn0_db": float(ebn0_db),
        "esn0_db": float(ebn0_to_esn0_db(ebn0_db, k)),
        "noise_variance": variance,
        "n_bits": count,
        "n_symbols": symbol_count,
        "bit_errors": errors,
        "symbol_errors": symbol_errors,
        "errors_per_bit_position": positions.tolist(),
        "ber": errors / count,
        "ser": symbol_errors / symbol_count,
        "ber_ci_lower": ber_low,
        "ber_ci_upper": ber_high,
        "ser_ci_lower": ser_low,
        "ser_ci_upper": ser_high,
        "confidence": confidence,
        "ber_interval_method": "CP par position + Bonferroni",
        "ser_interval_method": "Clopper-Pearson bilateral",
        "zero_symbol_error_upper_one_sided": (
            zero_error_upper_bound(symbol_count, confidence) if symbol_errors == 0 else None
        ),
        "ber_theory_exact": ber_awgn(ebn0_db, m),
        "ser_theory_exact": ser_awgn(ebn0_db, m),
        "ber_qam_approx": qam_ber_nearest_neighbor(ebn0_db, m) if m in (16, 64) else None,
        "seed": int(seed),
        "batch_symbols": block,
        "numpy_version": np.__version__,
    }
