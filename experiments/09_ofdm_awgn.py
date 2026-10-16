"""OFDM sur AWGN : référence utile ou totale incluant CP, effectifs fixes."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab import generate_bits
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.metrics import ber_interval, binomial_interval
from ofdm_lab.ofdm_simulation import simulate_ofdm_awgn
from ofdm_lab.receiver import receive
from ofdm_lab.transmitter import transmit
from ofdm_lab.visualization import plot_ofdm_ber

ROOT = Path(__file__).resolve().parents[1]


def run():
    params = json.loads((ROOT / "configs/ofdm_awgn.json").read_text(encoding="utf-8"))
    cases = [
        (m, cp, ref, db)
        for m in params["orders"]
        for cp in params["cp_lengths"]
        for ref in params["energy_references"]
        for db in params["ebn0_db"]
    ]
    sequences = np.random.SeedSequence(params["seed"]).spawn(len(cases))
    confidence = 1 - 0.01 / (2 * len(cases))
    rows = []
    ideal = []
    for (order, cp, reference, db), sequence in zip(cases, sequences, strict=True):
        config = OFDMConfig(params["n_fft"], params["n_active"], cp, order, params["spacing_hz"])
        row = simulate_ofdm_awgn(
            config, db, params["n_ofdm_symbols"], int(sequence.generate_state(1)[0]), reference
        )
        bl, bh = ber_interval(row["errors_per_bit_position"], row["n_symbols"], confidence)
        sl, sh = binomial_interval(row["symbol_errors"], row["n_symbols"], confidence)
        row.update(
            ber_validation_lower=bl,
            ber_validation_upper=bh,
            ser_validation_lower=sl,
            ser_validation_upper=sh,
            ber_validation_passed=bl <= row["ber_theory_exact"] <= bh,
            ser_validation_passed=sl <= row["ser_theory_exact"] <= sh,
            validation_confidence_per_point=confidence,
            root_seed=params["seed"],
        )
        rows.append(row)
    for order in params["orders"]:
        for cp in params["cp_lengths"]:
            config = OFDMConfig(
                params["n_fft"], params["n_active"], cp, order, params["spacing_hz"]
            )
            bits = generate_bits(100 * config.bits_per_ofdm_symbol, params["seed"])
            recovered = receive(transmit(bits, config).waveform, config).bits
            ideal.append(
                {
                    "order": order,
                    "cp_length": cp,
                    "n_bits": int(bits.size),
                    "bit_errors": int(np.count_nonzero(bits != recovered)),
                }
            )
    frame = pd.DataFrame(rows)
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(exist_ok=True, parents=True)
    export = frame.copy()
    export["errors_per_bit_position"] = export.errors_per_bit_position.map(json.dumps)
    export.to_csv(ROOT / "results/datasets/ofdm_awgn.csv", index=False)
    (ROOT / "results/reports/ofdm_awgn.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    summary = {
        "n_points": len(rows),
        "total_bits": int(frame.n_bits.sum()),
        "ideal_cases": ideal,
        "all_ideal_passed": all(r["bit_errors"] == 0 for r in ideal),
        "all_ber_validation_passed": bool(frame.ber_validation_passed.all()),
        "all_ser_validation_passed": bool(frame.ser_validation_passed.all()),
        "familywise_confidence_at_least": 0.99,
        "cp_penalties_db": {
            str(cp): float(10 * np.log10(1 + cp / params["n_fft"])) for cp in params["cp_lengths"]
        },
        "numpy_version": np.__version__,
    }
    (ROOT / "results/reports/ofdm_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    plot_ofdm_ber(frame, ROOT / "results/figures/09_ofdm_awgn.png")
    print(json.dumps(summary, indent=2))
    if not all(
        summary[k]
        for k in ["all_ideal_passed", "all_ber_validation_passed", "all_ser_validation_passed"]
    ):
        raise RuntimeError("Validation OFDM échouée ; investiguer avant phase suivante.")


if __name__ == "__main__":
    run()
