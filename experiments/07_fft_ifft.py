"""Inversion FFT/IFFT, Parseval et orthogonalité vérifiés numériquement."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab import generate_bits, modulate_qpsk
from ofdm_lab.transforms import fft, ifft, subcarrier_frequencies
from ofdm_lab.visualization import plot_transform_experiment

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = json.loads((ROOT / "configs/fft.json").read_text(encoding="utf-8"))
    size = config["n_fft"]
    spectrum = modulate_qpsk(generate_bits(2 * size, config["seed"]))
    waveform = ifft(spectrum)
    restored = fft(waveform)
    n = np.arange(size)
    basis = np.exp(2j * np.pi * n[:, None] * n[None, :] / size) / np.sqrt(size)
    gram = basis.conj().T @ basis
    fs = size * config["spacing_hz"]
    summary = {
        **config,
        "sample_rate_hz": fs,
        "useful_duration_s": 1 / config["spacing_hz"],
        "max_inverse_error": float(np.max(abs(restored - spectrum))),
        "frequency_energy": float(np.sum(abs(spectrum) ** 2)),
        "time_energy": float(np.sum(abs(waveform) ** 2)),
        "max_orthogonality_error": float(np.max(abs(gram - np.eye(size)))),
        "normalization": "ortho (unitaire)",
        "numpy_version": np.__version__,
    }
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(exist_ok=True, parents=True)
    pd.DataFrame(
        {"sample_index": n, "time_s": n / fs, "I": waveform.real, "Q": waveform.imag}
    ).to_csv(ROOT / "results/datasets/fft_time.csv", index=False)
    pd.DataFrame(
        {
            "fft_index": n,
            "frequency_hz": subcarrier_frequencies(size, config["spacing_hz"]),
            "I": spectrum.real,
            "Q": spectrum.imag,
        }
    ).to_csv(ROOT / "results/datasets/fft_frequency.csv", index=False)
    (ROOT / "results/reports/fft.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    plot_transform_experiment(
        waveform, spectrum, gram, fs, ROOT / "results/figures/07_fft_ifft.png"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
