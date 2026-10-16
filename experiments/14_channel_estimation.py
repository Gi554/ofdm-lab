"""Pilotes en peigne LS + interpolation ; H vrai réservé aux témoins et mesures."""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.channels import frequency_response
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout, estimate_channel_ls
from ofdm_lab.pilot_simulation import simulate_pilot_channel


def run():
    params = json.loads((ROOT / "configs/estimation.json").read_text(encoding="utf-8"))
    _, fixed, fading = load_channels()
    channels = [("awgn", np.array([1.0])), ("fixed", fixed), ("rayleigh_static", fading)]
    trial_count = (
        len(channels)
        * len(params["orders"])
        * len(params["pilot_spacings"])
        * len(params["ebn0_db"])
    )
    seeds = iter(np.random.SeedSequence(params["seed"]).generate_state(trial_count))
    rows, profiles = [], []
    for name, taps in channels:
        for order in params["orders"]:
            for spacing in params["pilot_spacings"]:
                layout = PilotLayout(OFDMConfig(order=order), spacing)
                for db in params["ebn0_db"]:
                    trial = simulate_pilot_channel(
                        layout,
                        taps,
                        db,
                        params["n_ofdm_symbols"],
                        int(next(seeds)),
                        params["energy_reference"],
                    )
                    rows.extend([dict(channel=name, **row) for row in trial])
        # Biais d'interpolation exact sans bruit, aucune décision ni donnée nécessaire.
        for spacing in params["pilot_spacings"]:
            layout = PilotLayout(OFDMConfig(), spacing)
            truth = frequency_response(taps, 64)
            grid = np.zeros((1, 64), complex)
            grid[:, layout.config.active_indices[layout.pilot_positions]] = (
                truth[layout.config.active_indices[layout.pilot_positions]] * layout.pilot_symbols
            )
            estimated = estimate_channel_ls(grid, layout)[0]
            for position, index in enumerate(layout.config.active_indices):
                profiles.append(
                    dict(
                        channel=name,
                        spacing=spacing,
                        signed_bin=int(index if index < 32 else index - 64),
                        pilot=bool(position in layout.pilot_positions),
                        true_real=float(truth[index].real),
                        true_imag=float(truth[index].imag),
                        estimated_real=float(estimated[index].real),
                        estimated_imag=float(estimated[index].imag),
                    )
                )
    frame = pd.DataFrame(rows)
    pilot = frame[frame.method == "pilot_linear"].copy()
    # Inégalité de Chebyshev + union : couverture simultanée >=99 % des moyennes MSE.
    pilot["mse_validation_radius"] = np.sqrt(pilot.channel_mse_mean_variance * len(pilot) / 0.01)
    pilot["mse_validation_passed"] = (
        abs(pilot.channel_mse_data - pilot.channel_mse_theory) <= pilot.mse_validation_radius
    )
    summary = dict(
        seed=params["seed"],
        numpy_version=np.__version__,
        n_trials=len(frame) // 3,
        n_measurements=len(frame),
        unique_transmitted_bits=int(frame[frame.method == "perfect"].n_bits.sum()),
        energy_reference=params["energy_reference"],
        all_mse_validation_passed=bool(pilot.mse_validation_passed.all()),
        mse_validation="Chebyshev + union; simultaneous coverage >=99%; conservative",
        channel_assumptions="static realization, CP sufficient, perfect timing, zero CFO",
        estimation="per-frame LS + linear interpolation independently in each active half-band",
        n_pilots_by_spacing={
            str(s): int(PilotLayout(OFDMConfig(), s).pilot_positions.size)
            for s in params["pilot_spacings"]
        },
    )
    for folder in ["datasets", "reports", "figures"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    exported = frame.copy()
    for column in ["pilot_positions", "pilot_symbols", "channel_taps", "errors_by_carrier_bit"]:
        exported[column] = exported[column].map(json.dumps)
    exported.to_csv(ROOT / "results/datasets/channel_estimation.csv", index=False)
    pilot[
        [
            "channel",
            "order",
            "pilot_spacing",
            "ebn0_db",
            "channel_mse_data",
            "channel_mse_theory",
            "mse_validation_radius",
            "mse_validation_passed",
        ]
    ].to_csv(ROOT / "results/datasets/estimation_validation.csv", index=False)
    profile = pd.DataFrame(profiles)
    profile.to_csv(ROOT / "results/datasets/estimation_profiles.csv", index=False)
    (ROOT / "results/reports/channel_estimation.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for col, (name, _) in enumerate(channels):
        subset = frame[(frame.channel == name) & (frame.order == 16) & (frame.pilot_spacing == 4)]
        for method, group in subset.groupby("method", sort=False):
            axes[0, col].errorbar(
                group.ebn0_db,
                group.ber,
                yerr=[group.ber - group.ber_ci_lower, group.ber_ci_upper - group.ber],
                fmt="o-",
                capsize=2,
                label=method,
            )
        axes[0, col].set(
            title=name + " — BER données, pas pilote 4",
            xlabel="Eb total/N0 par bit de données (dB)",
            ylabel="BER et IC conservateur 95 %",
        )
        for spacing, group in pilot[(pilot.channel == name) & (pilot.order == 16)].groupby(
            "pilot_spacing"
        ):
            axes[1, col].semilogy(
                group.ebn0_db, group.channel_mse_data, "o-", label=f"LS interpolé, pas {spacing}"
            )
            axes[1, col].semilogy(
                group.ebn0_db,
                group.channel_mse_theory,
                "--",
                color=axes[1, col].lines[-1].get_color(),
                alpha=0.7,
            )
        axes[1, col].set(
            title=name + " — MSE sur les données",
            xlabel="Eb total/N0 par bit de données (dB)",
            ylabel="MSE canal ; pointillé = espérance analytique",
        )
    for ax in axes.ravel():
        ax.grid(which="both", alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/14_channel_estimation.png", dpi=160)
    plt.close(fig)
    print(json.dumps(summary, indent=2))
    print(
        frame[(frame.order == 16) & (frame.pilot_spacing == 4) & (frame.ebn0_db == 18)][
            [
                "channel",
                "method",
                "n_bits",
                "bit_errors",
                "ber",
                "channel_mse_data",
                "channel_mse_theory",
                "overhead_factor",
            ]
        ].to_string(index=False)
    )
    if not summary["all_mse_validation_passed"]:
        raise RuntimeError("MSE hors enveloppe de validation ; investiguer.")


if __name__ == "__main__":
    run()
