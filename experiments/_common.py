"""Exécution commune des expériences fondamentales, depuis toute arborescence."""

import csv
import json
from pathlib import Path

import numpy as np

from ofdm_lab import demodulate_bpsk, demodulate_qpsk, generate_bits, modulate_bpsk, modulate_qpsk
from ofdm_lab.visualization import plot_bits, plot_constellation

ROOT = Path(__file__).resolve().parents[1]


def run(kind):
    config = json.loads((ROOT / "configs/fundamentals.json").read_text())
    bits = generate_bits(config["n_bits"], config["seed"])
    out = ROOT / "results"
    for folder in ["figures", "datasets", "reports"]:
        (out / folder).mkdir(parents=True, exist_ok=True)
    if kind == "binary_generation":
        plot_bits(bits, out / "figures/01_binary_generation.png")
        data = bits[:, None]
        header = ["bit"]
        summary = {
            "n_bits": int(bits.size),
            "ones": int(bits.sum()),
            "fraction_ones": float(bits.mean()),
        }
    else:
        qpsk = kind == "qpsk"
        mod, demod = (modulate_qpsk, demodulate_qpsk) if qpsk else (modulate_bpsk, demodulate_bpsk)
        symbols = mod(bits)
        recovered = demod(symbols)
        ideal_bits = np.array([0, 0, 0, 1, 1, 1, 1, 0]) if qpsk else np.array([0, 1])
        labels = ["00", "01", "11", "10"] if qpsk else ["0", "1"]
        number = "03" if qpsk else "02"
        plot_constellation(
            mod(ideal_bits),
            labels,
            kind.upper() + " — Es = 1",
            out / f"figures/{number}_{kind}.png",
        )
        data = np.column_stack((symbols.real, symbols.imag))
        header = ["I", "Q"]
        errors = int(np.count_nonzero(bits != recovered))
        summary = {
            "n_bits": int(bits.size),
            "n_symbols": int(symbols.size),
            "bit_errors": errors,
            "ber_observed": errors / bits.size,
            "mean_symbol_energy": float(np.mean(np.abs(symbols) ** 2)),
            "channel": "ideal, sans bruit, phase connue",
        }
    with (out / f"datasets/{kind}.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    summary.update(seed=config["seed"], numpy_version=np.__version__)
    (out / f"reports/{kind}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
