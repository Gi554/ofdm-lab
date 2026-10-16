"""Canaux fixe et Rayleigh : réponses et moments sur un ensemble indépendant."""

import json

import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.channels import channel_memory, frequency_response, rayleigh_channel
from ofdm_lab.visualization import plot_channel_profiles


def run():
    params, fixed, fading = load_channels()
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    seeds = np.random.SeedSequence(params["seed"] + 2).spawn(5000)
    samples = np.array(
        [
            rayleigh_channel(
                params["rayleigh_delays"], params["rayleigh_powers"], int(seed.generate_state(1)[0])
            )
            for seed in seeds
        ]
    )
    energies = np.sum(abs(samples) ** 2, axis=1)
    rows = []
    for name, h in [("fixed", fixed), ("rayleigh_static", fading)]:
        response = frequency_response(h, params["n_fft"])
        rows.append(
            {
                "channel": name,
                "memory_samples": channel_memory(h),
                "impulse_energy": float(np.sum(abs(h) ** 2)),
                "min_response_magnitude": float(np.min(abs(response))),
                "max_response_magnitude": float(np.max(abs(response))),
            }
        )
        pd.DataFrame({"delay_samples": np.arange(h.size), "I": h.real, "Q": h.imag}).to_csv(
            ROOT / f"results/datasets/channel_{name}.csv", index=False
        )
    pd.DataFrame({"realization": np.arange(len(energies)), "energy": energies}).to_csv(
        ROOT / "results/datasets/rayleigh_energies.csv", index=False
    )
    summary = {
        "channels": rows,
        "rayleigh_realizations": len(energies),
        "rayleigh_mean_energy": float(energies.mean()),
        "rayleigh_std_energy": float(energies.std()),
        "expected_mean_energy": 1.0,
        "rayleigh_realization_seed": params["seed"] + 1,
        "ensemble_root_seed": params["seed"] + 2,
        "numpy_version": np.__version__,
    }
    (ROOT / "results/reports/multipath.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    plot_channel_profiles(
        fixed,
        fading,
        energies,
        params["n_fft"] * params["spacing_hz"],
        ROOT / "results/figures/11_multipath_channel.png",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
