"""Allocation, signal temporel avec CP et DSP estimée du véritable signal OFDM."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab import generate_bits
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.transforms import subcarrier_frequencies
from ofdm_lab.transmitter import transmit
from ofdm_lab.visualization import plot_ofdm_transmission

ROOT = Path(__file__).resolve().parents[1]


def run():
    params = json.loads((ROOT / "configs/ofdm.json").read_text(encoding="utf-8"))
    config = OFDMConfig(**{k: v for k, v in params.items() if k not in ("seed", "n_ofdm_symbols")})
    bits = generate_bits(params["n_ofdm_symbols"] * config.bits_per_ofdm_symbol, params["seed"])
    tx = transmit(bits, config)
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(exist_ok=True, parents=True)
    n = np.arange(min(tx.waveform.size, 2 * (config.n_fft + config.cp_length)))
    pd.DataFrame(
        {
            "sample_index": n,
            "time_s": n / config.sample_rate_hz,
            "I": tx.waveform[n].real,
            "Q": tx.waveform[n].imag,
        }
    ).to_csv(ROOT / "results/datasets/ofdm_time.csv", index=False)
    pd.DataFrame(
        {
            "fft_index": np.arange(config.n_fft),
            "frequency_hz": subcarrier_frequencies(config.n_fft, config.spacing_hz),
            "I": tx.grid[0].real,
            "Q": tx.grid[0].imag,
        }
    ).to_csv(ROOT / "results/datasets/ofdm_grid.csv", index=False)
    summary = {
        **params,
        "n_bits": int(bits.size),
        "waveform_samples": int(tx.waveform.size),
        "mean_useful_energy": float(np.sum(abs(tx.useful) ** 2, axis=1).mean()),
        "mean_total_energy": float(np.sum(abs(tx.with_cp) ** 2, axis=1).mean()),
        "expected_useful_energy": float(config.n_active),
        "expected_total_energy": config.n_active * config.cp_energy_factor,
        "sample_rate_hz": config.sample_rate_hz,
        "numpy_version": np.__version__,
    }
    (ROOT / "results/reports/ofdm_transmitter.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    plot_ofdm_transmission(tx, config, ROOT / "results/figures/08_ofdm_transmitter.png")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
