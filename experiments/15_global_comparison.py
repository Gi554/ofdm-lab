"""Comparaison globale à Eb total, occupation et fréquence d'échantillonnage fixés."""

import itertools
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.channels import channel_memory
from ofdm_lab.comparison import simulate_comparison
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout
from ofdm_lab.metrics import mean_binomial_interval


def run():
    params = json.loads((ROOT / "configs/comparison.json").read_text(encoding="utf-8"))
    _, fixed, fading = load_channels()
    channels = [("awgn", np.array([1.0])), ("fixed", fixed), ("rayleigh_static", fading)]
    cases = list(
        itertools.product(
            channels,
            params["orders"],
            params["ebn0_db"],
            params["fft_sizes"],
            params["cp_lengths"],
            params["pilot_spacings"],
        )
    )
    seeds = np.random.SeedSequence(params["seed"]).generate_state(len(cases))
    comparisons = sum(cp >= channel_memory(channel[1]) for channel, _, _, _, cp, _ in cases)
    rows, validation = [], []
    paired = True
    for case, seed in zip(cases, seeds, strict=True):
        (name, taps), order, db, size, cp, pitch = case
        config = OFDMConfig(size, size * 13 // 16, cp, order, params["sample_rate_hz"] / size)
        layout = PilotLayout(config, pitch)
        trial = simulate_comparison(layout, taps, db, params["n_ofdm_symbols"], int(seed))
        paired &= (
            trial[1]["errors_by_carrier_bit"] == trial[2]["errors_by_carrier_bit"]
            and trial[3]["errors_by_carrier_bit"] == trial[4]["errors_by_carrier_bit"]
        )
        rows.extend([dict(channel=name, **row) for row in trial])
        if trial[1]["cp_sufficient"]:
            row = trial[1]
            low, high = mean_binomial_interval(
                np.array(row["errors_by_carrier_bit"]).ravel(),
                params["n_ofdm_symbols"],
                1 - 0.01 / comparisons,
            )
            validation.append(
                dict(
                    channel=name,
                    order=order,
                    n_fft=size,
                    cp_length=cp,
                    pilot_spacing=pitch,
                    ebn0_db=db,
                    ber_observed=row["ber"],
                    ber_theory=row["ber_theory_conditional"],
                    validation_lower=low,
                    validation_upper=high,
                    passed=low <= row["ber_theory_conditional"] <= high,
                )
            )
    frame = pd.DataFrame(rows)
    checks = pd.DataFrame(validation)
    summary = dict(
        seed=params["seed"],
        numpy_version=np.__version__,
        n_trials=len(cases),
        n_measurements=len(rows),
        unique_transmitted_bits=int(frame[frame.method == "perfect_zf"].n_bits.sum()),
        n_sufficient_cp_trials=int(frame[frame.method == "perfect_zf"].cp_sufficient.sum()),
        conditional_ber_comparisons=comparisons,
        all_conditional_ber_passed=bool(checks.passed.all()),
        familywise_confidence_at_least=0.99,
        paired_zf_mmse_error_counts_identical=bool(paired),
        sample_rate_hz=params["sample_rate_hz"],
        occupation_fraction=13 / 16,
        energy_reference="total including coherent pilots and CP",
        timing="perfect; CFO zero",
        rayleigh="one static realization, conditional results",
    )
    for folder in ["datasets", "reports", "figures"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    exported = frame.copy()
    for column in ["channel_taps", "errors_by_carrier_bit", "pilot_positions"]:
        exported[column] = exported[column].map(json.dumps)
    exported.to_csv(ROOT / "results/datasets/global_comparison.csv", index=False)
    checks.to_csv(ROOT / "results/datasets/global_validation.csv", index=False)
    score = frame[
        (frame.n_fft == 64)
        & (frame.cp_length == 16)
        & (frame.pilot_spacing == 4)
        & (frame.ebn0_db == 18)
    ]
    score[
        [
            "channel",
            "order",
            "method",
            "n_bits",
            "bit_errors",
            "ber",
            "ber_ci_lower",
            "ber_ci_upper",
            "symbol_mse",
            "channel_mse_data",
            "payload_rate_bps",
            "overhead_factor",
        ]
    ].to_csv(ROOT / "results/datasets/global_scorecard.csv", index=False)
    (ROOT / "results/reports/global_comparison.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    plot(frame)
    print(json.dumps(summary, indent=2))
    print(
        score[(score.order == 16)][
            ["channel", "method", "n_bits", "bit_errors", "ber", "symbol_mse", "channel_mse_data"]
        ].to_string(index=False)
    )
    if not all([summary["all_conditional_ber_passed"], paired]):
        raise RuntimeError("Échec de validation globale ; investiguer.")


def plot(frame):
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    common = frame[
        (frame.channel == "fixed") & (frame.cp_length == 16) & (frame.pilot_spacing == 4)
    ]
    for (order, method), group in common[
        (common.n_fft == 64) & common.method.isin(["perfect_zf", "pilot_zf"])
    ].groupby(["order", "method"]):
        axes[0, 0].plot(
            group.ebn0_db,
            group.ber,
            "o-" if method == "perfect_zf" else "s--",
            label=f"M={order} / " + method,
        )
    axes[0, 0].set(
        title="Modulation : FIR fixe, N64, CP16, pas4",
        xlabel="Eb total/N0 (dB)",
        ylabel="BER données observé",
    )
    for pitch, group in frame[
        (frame.channel == "fixed")
        & (frame.cp_length == 16)
        & (frame.order == 16)
        & (frame.ebn0_db == 18)
        & (frame.method == "pilot_zf")
    ].groupby("pilot_spacing"):
        group = group.sort_values("n_fft")
        axes[0, 1].semilogy(group.n_fft, group.channel_mse_data, "o-", label=f"pas {pitch}")
    axes[0, 1].set(
        title="FFT et densité : FIR fixe, M16, CP16, 18 dB",
        xlabel="Taille FFT, Fs=960 kHz",
        ylabel="MSE canal estimé",
    )
    selection = frame[
        (frame.channel == "fixed")
        & (frame.n_fft == 64)
        & (frame.pilot_spacing == 4)
        & (frame.order == 16)
        & (frame.ebn0_db == 18)
    ]
    for method, group in selection[
        selection.method.isin(["none", "perfect_zf", "pilot_zf"])
    ].groupby("method"):
        axes[0, 2].plot(group.cp_length, group.ber, "o-", label=method)
    axes[0, 2].set(
        title="CP court descriptif (mémoire FIR=6)",
        xlabel="Longueur CP (échantillons)",
        ylabel="BER données observé",
    )
    selection = frame[
        (frame.n_fft == 64)
        & (frame.cp_length == 16)
        & (frame.pilot_spacing == 4)
        & (frame.order == 16)
        & (frame.ebn0_db == 18)
    ]
    names = ["awgn", "fixed", "rayleigh_static"]
    for i, method in enumerate(["none", "perfect_zf", "pilot_zf"]):
        group = selection[selection.method == method].set_index("channel").loc[names]
        axes[1, 0].bar(np.arange(3) + (i - 1) * 0.24, group.ber, width=0.24, label=method)
    axes[1, 0].set(
        xticks=np.arange(3),
        xticklabels=names,
        title="Canal : M16, N64, CP16, pas4, 18 dB",
        ylabel="BER données observé",
    )
    for method, group in common[
        (common.n_fft == 64) & (common.order == 16) & (common.method != "none")
    ].groupby("method"):
        axes[1, 1].semilogy(group.ebn0_db, group.symbol_mse, "o-", label=method)
    axes[1, 1].set(
        title="Estimation et égaliseur : FIR fixe, M16",
        xlabel="Eb total/N0 (dB)",
        ylabel="MSE des symboles estimés",
    )
    for pitch, group in frame[
        (frame.channel == "awgn")
        & (frame.cp_length == 16)
        & (frame.order == 16)
        & (frame.ebn0_db == 18)
        & (frame.method == "perfect_zf")
    ].groupby("pilot_spacing"):
        group = group.sort_values("n_fft")
        axes[1, 2].plot(group.n_fft, group.payload_rate_bps / 1e6, "o-", label=f"pas {pitch}")
    axes[1, 2].set(
        title="Débit utile, M16, CP16, sans codage",
        xlabel="Taille FFT, Fs=960 kHz",
        ylabel="Débit données (Mbit/s)",
    )
    for ax in axes.ravel():
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle(
        "Comparaisons conditionnelles — points observés ; détails et IC par ligne dans les CSV",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/15_global_comparison.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    run()
