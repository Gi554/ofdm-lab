"""CFO constant, timing connu : ICI, phase et correction par corrélation CP."""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.channels import apply_multipath, channel_memory, frequency_response
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.noise import add_awgn
from ofdm_lab.ofdm_simulation import energy_budget
from ofdm_lab.receiver import receive
from ofdm_lab.synchronization import apply_frequency_offset, cfo_tone_response, estimate_cfo_cp
from ofdm_lab.transmitter import transmit


def burst(config, taps, frames, offset, ebn0, seed):
    data_seed, noise_seed = seed.spawn(2)
    bits = np.random.default_rng(data_seed).integers(
        0, 2, frames * config.bits_per_ofdm_symbol, dtype=np.uint8
    )
    tx = transmit(bits, config)
    channel = apply_multipath(tx.waveform, taps)[: tx.waveform.size]
    shifted = apply_frequency_offset(channel, offset, config.n_fft)
    n0 = energy_budget(config, ebn0, "useful")["noise_variance"] if ebn0 is not None else 0
    return bits, tx, add_awgn(shifted, n0, noise_seed)


def run():
    options = json.loads((ROOT / "configs/synchronization.json").read_text(encoding="utf-8"))
    _, fixed, _ = load_channels()
    seeds = iter(np.random.SeedSequence(options["seed"]).spawn(1000))
    rows, estimates, ideal = [], [], []
    unique_bits = 0
    for name, taps in [("awgn", np.array([1])), ("fixed", fixed)]:
        for order in options["orders"]:
            config = OFDMConfig(order=order)
            h = frequency_response(taps, config.n_fft)
            for offset in options["offsets"]:
                for ebn0 in options["ebn0_db"]:
                    bits, tx, noisy = burst(
                        config, taps, options["n_ofdm_symbols"], offset, ebn0, next(seeds)
                    )
                    unique_bits += bits.size
                    estimate = estimate_cfo_cp(noisy, config, channel_memory=channel_memory(taps))
                    for method, correction in [
                        ("none", 0),
                        ("cp_estimated", estimate.normalized_offset),
                        ("oracle", offset),
                    ]:
                        corrected = apply_frequency_offset(noisy, -correction, config.n_fft)
                        rx = receive(corrected, config, channel_response=h, equalizer="zf")
                        errors = int(np.count_nonzero(rx.bits != bits))
                        rows.append(
                            dict(
                                channel=name,
                                order=order,
                                n_fft=config.n_fft,
                                n_active=config.n_active,
                                cp_length=config.cp_length,
                                channel_memory=channel_memory(taps),
                                offset=offset,
                                offset_hz=offset * config.spacing_hz,
                                ebn0_db=ebn0,
                                energy_reference="useful",
                                method=method,
                                estimated_offset=estimate.normalized_offset,
                                residual_offset=offset - correction,
                                coherence=estimate.coherence,
                                n_pairs=estimate.n_pairs,
                                n_bits=int(bits.size),
                                bit_errors=errors,
                                ber=errors / bits.size,
                                mse=float(
                                    np.mean(
                                        abs(
                                            rx.equalized_symbols
                                            - tx.grid[:, config.active_indices].ravel()
                                        )
                                        ** 2
                                    )
                                ),
                                seed=options["seed"],
                                interval_method=(
                                    "aucun : estimation commune et rotation sur le burst"
                                ),
                            )
                        )
            # Validation sans bruit, CFO dans la plage identifiable, même canal FIR.
            for offset in [-0.3, 0, 0.3]:
                bits, tx, received = burst(config, taps, 100, offset, None, next(seeds))
                est = estimate_cfo_cp(received, config, channel_memory=channel_memory(taps))
                rx = receive(
                    apply_frequency_offset(received, -est.normalized_offset, config.n_fft),
                    config,
                    channel_response=h,
                    equalizer="zf",
                )
                ideal.append(
                    dict(
                        channel=name,
                        order=order,
                        offset=offset,
                        estimate=est.normalized_offset,
                        bit_errors=int(np.count_nonzero(bits != rx.bits)),
                    )
                )
        config = OFDMConfig()
        for ebn0 in options["estimation_ebn0_db"]:
            for trial in range(options["estimation_trials"]):
                _, _, received = burst(
                    config,
                    taps,
                    options["estimation_frames"],
                    options["estimation_offset"],
                    ebn0,
                    next(seeds),
                )
                result = estimate_cfo_cp(received, config, channel_memory=channel_memory(taps))
                error = result.normalized_offset - options["estimation_offset"]
                estimates.append(
                    dict(
                        channel=name,
                        ebn0_db=ebn0,
                        trial=trial,
                        estimate=result.normalized_offset,
                        error=error,
                        wrapped_error=(error + 0.5) % 1 - 0.5,
                        coherence=result.coherence,
                    )
                )
    frame, trials = pd.DataFrame(rows), pd.DataFrame(estimates)
    leakage = pd.DataFrame(
        [
            dict(
                offset=float(e),
                desired_power=float(abs(cfo_tone_response(e, 64)[0]) ** 2),
                ici_power=float(np.sum(abs(cfo_tone_response(e, 64)[1:]) ** 2)),
            )
            for e in np.linspace(0, 1, 101)
        ]
    )
    stats = (
        trials.groupby(["channel", "ebn0_db"])
        .agg(
            bias=("error", "mean"),
            rmse=("error", lambda x: float(np.sqrt(np.mean(x**2)))),
            wrapped_rmse=("wrapped_error", lambda x: float(np.sqrt(np.mean(x**2)))),
        )
        .reset_index()
    )
    for folder in ["datasets", "reports", "figures"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    for name, data in [
        ("frequency_offset", frame),
        ("cfo_estimates", trials),
        ("cfo_estimation_summary", stats),
        ("cfo_leakage", leakage),
    ]:
        data.to_csv(ROOT / f"results/datasets/{name}.csv", index=False)
    summary = dict(
        seed=options["seed"],
        numpy_version=np.__version__,
        n_bursts=len(rows) // 3,
        unique_transmitted_bits=int(unique_bits),
        n_measurements=len(rows),
        estimation_trials=len(estimates),
        noiseless_cases=ideal,
        all_noiseless_corrections_passed=all(
            r["bit_errors"] == 0 and abs(r["estimate"] - r["offset"]) < 1e-12 for r in ideal
        ),
        cp_capture_interval="[-0.5,0.5] modulo 1; endpoints ambiguous",
        channel_knowledge="perfect H for ZF; known memory bound for CP correlation",
        estimation_statistics=stats.to_dict(orient="records"),
    )
    (ROOT / "results/reports/frequency_offset.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes[0, 0].plot(leakage.offset, leakage.desired_power, label="Porteuse initiale")
    axes[0, 0].plot(leakage.offset, leakage.ici_power, label="Fuite vers les autres cases")
    axes[0, 0].set(
        xlabel="CFO normalisé ε = Δf/Δf porteuses",
        ylabel="Fraction de puissance",
        title="Porteuse isolée, N=64, sans bruit",
    )
    for name, group in frame[(frame.order == 16) & (frame.ebn0_db == 24)].groupby("channel"):
        for method, values in group.groupby("method"):
            # Échelle linéaire : zéro observé ne signifie pas BER théorique nul.
            axes[0, 1].plot(values.offset, values.ber, "o-", label=name + " / " + method)
    axes[0, 1].set(
        xlabel="CFO normalisé ε",
        ylabel="BER observé, descriptif",
        title="16-QAM, Eb utile/N0 = 24 dB",
    )
    for name, group in stats.groupby("channel"):
        axes[1, 0].semilogy(group.ebn0_db, group.rmse, "o-", label=name)
    axes[1, 0].set(
        xlabel="Eb utile/N0 (dB)",
        ylabel="RMSE CFO normalisé",
        title="50 bursts indépendants de 20 trames ; ε=0,2",
    )
    # Phase théorique commune à chaque fenêtre FFT ; l’ICI reste présente.
    for offset in [0.05, 0.3]:
        starts = np.arange(10) * 80 + 16
        c0 = cfo_tone_response(offset, 64)[0]
        phase = np.unwrap(np.angle(c0 * np.exp(2j * np.pi * offset * starts / 64)))
        axes[1, 1].plot(np.arange(10), phase, "o-", label=f"ε={offset}")
    axes[1, 1].set(
        xlabel="Indice de symbole OFDM",
        ylabel="Phase commune déroulée (rad)",
        title="Rotation cumulée, origine au début du CP",
    )
    for ax in axes.ravel():
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/13_frequency_offset.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))
    if not summary["all_noiseless_corrections_passed"]:
        raise RuntimeError("Échec de correction CFO sans bruit.")


if __name__ == "__main__":
    run()
