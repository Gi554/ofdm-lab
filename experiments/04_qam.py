"""Comparer les alphabets QAM et vérifier leur transmission idéale reproductible."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab import demodulate_qam, generate_bits, modulate_qam
from ofdm_lab.visualization import plot_constellation

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = json.loads((ROOT / "configs/qam.json").read_text(encoding="utf-8"))
    count = config["n_bits"]
    bits = generate_bits(count, config["seed"])
    if count == 0:
        raise ValueError("L'expérience exige un nombre de bits strictement positif.")
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    rows = []
    for order in config["orders"]:
        k = int(order).bit_length() - 1
        shifts = np.arange(k - 1, -1, -1)
        labels = ((np.arange(order)[:, None] >> shifts) & 1).astype(np.uint8)
        alphabet = modulate_qam(labels.ravel(), order)
        symbols = modulate_qam(bits, order)
        recovered = demodulate_qam(symbols, order)
        bit_errors = int(np.count_nonzero(bits != recovered))
        symbol_errors = int(
            np.count_nonzero(np.any(bits.reshape(-1, k) != recovered.reshape(-1, k), axis=1))
        )
        text_labels = ["".join(str(int(b)) for b in label) for label in labels]
        plot_constellation(
            alphabet,
            text_labels,
            f"{order}-QAM Gray — Es = 1",
            ROOT / f"results/figures/04_{order}qam.png",
        )
        pd.DataFrame(
            {
                "bits_I_puis_Q": text_labels,
                "I": alphabet.real,
                "Q": alphabet.imag,
                "energy": abs(alphabet) ** 2,
            }
        ).to_csv(ROOT / f"results/datasets/{order}qam_alphabet.csv", index=False)
        rows.append(
            {
                "modulation": f"{order}-QAM",
                "bits_per_symbol": k,
                "n_bits": count,
                "n_symbols": int(symbols.size),
                "bit_errors": bit_errors,
                "symbol_errors": symbol_errors,
                "ber_observed": bit_errors / count,
                "ser_observed": symbol_errors / symbols.size,
                "alphabet_mean_energy": float(np.mean(abs(alphabet) ** 2)),
                "sample_mean_energy": float(np.mean(abs(symbols) ** 2)),
                "minimum_distance": float(
                    np.min(abs(alphabet[:, None] - alphabet[None, :])[~np.eye(order, dtype=bool)])
                ),
                "seed": config["seed"],
                "numpy_version": np.__version__,
                "channel": "ideal, sans bruit, phase connue",
            }
        )
    pd.DataFrame(rows).to_csv(ROOT / "results/datasets/qam_comparison.csv", index=False)
    (ROOT / "results/reports/qam.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(rows, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
