"""Comparer l'identité circulaire avec CP absent, court ou suffisant."""

import json

import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab import generate_bits
from ofdm_lab.channels import apply_multipath, channel_memory, frequency_response
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.metrics import count_errors
from ofdm_lab.receiver import receive
from ofdm_lab.transmitter import transmit
from ofdm_lab.visualization import plot_cp_identity


def run():
    params, h, _ = load_channels()
    rows = []
    for cp in params["cp_lengths"]:
        config = OFDMConfig(
            params["n_fft"], params["n_active"], cp, params["order"], params["spacing_hz"]
        )
        bits = generate_bits(params["n_ofdm_symbols"] * config.bits_per_ofdm_symbol, params["seed"])
        tx = transmit(bits, config)
        full = apply_multipath(tx.waveform, h)
        # La queue est conservée par le canal, puis exclue explicitement du burst attendu.
        rx = receive(full[: tx.waveform.size], config)
        target = tx.grid * frequency_response(h, config.n_fft)
        counts = count_errors(bits, rx.bits, config.bits_per_symbol)
        rows.append(
            {
                "cp_length": cp,
                "channel_memory": channel_memory(h),
                "cp_sufficient": cp >= channel_memory(h),
                "n_bits": int(bits.size),
                "bit_errors_uncorrected": counts.bit_errors,
                "ber_uncorrected": counts.ber,
                "relative_diagonal_error": float(
                    np.sum(abs(rx.grid - target) ** 2) / np.sum(abs(target) ** 2)
                ),
                "tail_samples": int(full.size - tx.waveform.size),
                "seed": params["seed"],
                "numpy_version": np.__version__,
            }
        )
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(ROOT / "results/datasets/cyclic_prefix.csv", index=False)
    (ROOT / "results/reports/cyclic_prefix.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    plot_cp_identity(frame, ROOT / "results/figures/10_cyclic_prefix.png")
    print(frame.to_string(index=False))
    if any(r["relative_diagonal_error"] > 1e-24 for r in rows if r["cp_sufficient"]):
        raise RuntimeError("Identité circulaire non vérifiée avec CP suffisant.")


if __name__ == "__main__":
    run()
