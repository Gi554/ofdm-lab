"""Mesurer la puissance AWGN et observer les constellations réellement bruitées."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab import generate_bits, modulate_bpsk, modulate_qam, modulate_qpsk
from ofdm_lab.noise import add_awgn, ebn0_to_esn0_db, noise_variance
from ofdm_lab.visualization import plot_constellation_clouds

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = json.loads((ROOT / "configs/awgn.json").read_text(encoding="utf-8"))
    bits = generate_bits(config["n_bits"], config["seed"])
    seeds = np.random.SeedSequence(config["seed"]).spawn(4 * len(config["ebn0_db"]))
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    rows = []
    for index, (name, k, mod) in enumerate(
        [
            ("BPSK", 1, modulate_bpsk),
            ("QPSK", 2, modulate_qpsk),
            ("16-QAM", 4, lambda b: modulate_qam(b, 16)),
            ("64-QAM", 6, lambda b: modulate_qam(b, 64)),
        ]
    ):
        labels = ((np.arange(2**k)[:, None] >> np.arange(k - 1, -1, -1)) & 1).ravel()
        ideal, transmitted = mod(labels), mod(bits)
        clouds = []
        for offset, ebn0 in enumerate(config["ebn0_db"]):
            seed = int(seeds[index * len(config["ebn0_db"]) + offset].generate_state(1)[0])
            target = noise_variance(ebn0, k)
            received = add_awgn(transmitted, target, seed)
            noise = received - transmitted
            measured = float(np.mean(abs(noise) ** 2))
            rows.append(
                {
                    "modulation": name,
                    "ebn0_db": ebn0,
                    "esn0_db": ebn0_to_esn0_db(ebn0, k),
                    "n_bits": int(bits.size),
                    "n_symbols": int(transmitted.size),
                    "target_noise_variance": target,
                    "measured_noise_power": measured,
                    "relative_power_error": (measured - target) / target,
                    "mean_noise_I": float(noise.real.mean()),
                    "mean_noise_Q": float(noise.imag.mean()),
                    "variance_I": float(noise.real.var()),
                    "variance_Q": float(noise.imag.var()),
                    "measured_snr_db": float(
                        10 * np.log10(np.mean(abs(transmitted) ** 2) / measured)
                    ),
                    "data_seed": config["seed"],
                    "noise_seed": seed,
                    "numpy_version": np.__version__,
                }
            )
            clouds.append((f"Eb/N0 = {ebn0} dB", received[: config["display_symbols"]]))
        plot_constellation_clouds(
            clouds,
            ideal,
            f"{name} — AWGN complexe circulaire",
            ROOT / f"results/figures/05_awgn_{name.lower()}.png",
        )
    pd.DataFrame(rows).to_csv(ROOT / "results/datasets/awgn.csv", index=False)
    (ROOT / "results/reports/awgn.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(
        pd.DataFrame(rows)[
            [
                "modulation",
                "ebn0_db",
                "target_noise_variance",
                "measured_noise_power",
                "relative_power_error",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    run()
