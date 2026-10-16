"""Comparaison appariée OFDM, ressources pilotes et énergie identiques entre modes."""

import numpy as np

from .channels import apply_multipath, channel_memory, frequency_response, impulse_response
from .estimation import estimate_channel_ls, pilot_energy_budget, transmit_pilots
from .metrics import mean_binomial_interval
from .noise import _positive_integer, add_awgn
from .receiver import receive
from .theory import ber_awgn


def simulate_comparison(layout, taps, ebn0_db, n_ofdm_symbols, seed):
    """Comparer none, perfect_zf/mmse et pilot_zf/mmse, gain de décision compensé.

    CFO nul et début connu. CP court accepté uniquement comme essai descriptif :
    H et H_hat restent des approximations diagonales, pas une inversion de l'ISI.
    Même pilote et même payload pour tous les modes, sans réaffecter les pilotes
    au témoin parfait. Référence Eb total incluant pilotes et CP déterministe.
    """
    frames = _positive_integer(n_ofdm_symbols, "Le nombre de trames")
    config = layout.config
    taps = impulse_response(taps)
    memory = channel_memory(taps)
    sufficient = config.cp_length >= memory
    truth = frequency_response(taps, config.n_fft)
    budget = pilot_energy_budget(layout, ebn0_db, "total")
    data_seed, noise_seed = np.random.SeedSequence(seed).spawn(2)
    bits = np.random.default_rng(data_seed).integers(
        0, 2, frames * layout.bits_per_frame, dtype=np.uint8
    )
    tx = transmit_pilots(bits, layout)
    noisy = add_awgn(
        apply_multipath(tx.waveform, taps)[: tx.waveform.size], budget["noise_variance"], noise_seed
    )
    estimated = estimate_channel_ls(receive(noisy, config).grid, layout)
    positions = layout.data_positions
    indices = config.active_indices[positions]
    target = tx.grid[:, indices]
    theoretical = None
    if sufficient:
        effective = 10 * np.log10(
            abs(truth[indices]) ** 2 / (config.bits_per_symbol * budget["noise_variance"])
        )
        theoretical = float(np.mean([ber_awgn(db, config.order) for db in effective]))
    rows = []
    intervals = {}
    for method, response, equalizer in [
        ("none", None, "none"),
        ("perfect_zf", truth, "zf"),
        ("perfect_mmse", truth, "mmse"),
        ("pilot_zf", estimated, "zf"),
        ("pilot_mmse", estimated, "mmse"),
    ]:
        rx = receive(
            noisy,
            config,
            channel_response=response,
            equalizer=equalizer,
            noise_variance=budget["noise_variance"],
        )
        decided = rx.bits.reshape(frames, config.n_active, config.bits_per_symbol)[:, positions, :]
        errors = decided != bits.reshape(frames, positions.size, config.bits_per_symbol)
        counts = errors.sum(axis=0)
        lower = upper = None
        if sufficient:
            key = counts.tobytes()
            if key not in intervals:
                intervals[key] = mean_binomial_interval(counts.ravel(), frames, 0.95)
            lower, upper = intervals[key]
        model = np.ones(config.n_fft) if response is None else response
        symbols = rx.equalized_symbols.reshape(frames, config.n_active)[:, positions]
        rows.append(
            dict(
                **budget,
                method=method,
                equalizer=equalizer,
                estimation="none"
                if response is None
                else ("perfect" if method.startswith("perfect") else "ls_linear"),
                order=config.order,
                n_fft=config.n_fft,
                n_active=config.n_active,
                cp_length=config.cp_length,
                spacing_hz=config.spacing_hz,
                sample_rate_hz=config.sample_rate_hz,
                cp_sufficient=sufficient,
                channel_memory=memory,
                channel_taps=[[float(z.real), float(z.imag)] for z in taps],
                pilot_spacing=layout.spacing,
                n_ofdm_symbols=frames,
                ebn0_db=float(ebn0_db),
                n_bits=int(bits.size),
                bit_errors=int(errors.sum()),
                errors_by_carrier_bit=counts.tolist(),
                ber=float(errors.mean()),
                ber_ci_lower=lower,
                ber_ci_upper=upper,
                confidence=0.95 if sufficient else None,
                interval_method="Clopper-Pearson + Bonferroni par porteuse/bit"
                if sufficient
                else "aucun : ISI",
                ber_theory_conditional=theoretical if method.startswith("perfect") else None,
                channel_mse_data=float(np.mean(abs(model[..., indices] - truth[indices]) ** 2)),
                symbol_mse=float(np.mean(abs(symbols - target) ** 2)),
                pilot_positions=layout.pilot_positions.tolist(),
                seed=int(seed),
                numpy_version=np.__version__,
            )
        )
    return rows
