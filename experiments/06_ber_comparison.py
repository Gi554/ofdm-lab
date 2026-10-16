"""Courbes BER/SER reproductibles : effectifs fixes et références AWGN exactes."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ofdm_lab.metrics import ber_interval, binomial_interval
from ofdm_lab.simulation import simulate_awgn
from ofdm_lab.theory import ber_awgn, qam_ber_nearest_neighbor, ser_awgn
from ofdm_lab.visualization import plot_error_curves, plot_qam_approximation

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = json.loads((ROOT / "configs/ber.json").read_text(encoding="utf-8"))
    pairs = [(m, db) for m in config["orders"] for db in config["ebn0_db"]]
    if not pairs:
        raise ValueError("La configuration doit contenir des modulations et des valeurs Eb/N0.")
    sequences = np.random.SeedSequence(config["seed"]).spawn(len(pairs))
    rows = []
    # Garantie simultanée d'au moins 99 % sur toutes les comparaisons BER et SER.
    validation_confidence = 1 - 0.01 / (2 * len(pairs))
    for (order, db), sequence in zip(pairs, sequences, strict=True):
        row = simulate_awgn(
            order,
            db,
            config["n_bits_per_point"],
            seed=int(sequence.generate_state(1)[0]),
            batch_symbols=config["batch_symbols"],
            confidence=config["confidence"],
        )
        bl, bh = ber_interval(
            row["errors_per_bit_position"], row["n_symbols"], validation_confidence
        )
        sl, sh = binomial_interval(row["symbol_errors"], row["n_symbols"], validation_confidence)
        row.update(
            ber_validation_lower=bl,
            ber_validation_upper=bh,
            ser_validation_lower=sl,
            ser_validation_upper=sh,
            validation_confidence_per_point=validation_confidence,
            ber_theory_in_validation_interval=bl <= row["ber_theory_exact"] <= bh,
            ser_theory_in_validation_interval=sl <= row["ser_theory_exact"] <= sh,
            precision_flag="moins de 100 erreurs binaires" if row["bit_errors"] < 100 else "",
            root_seed=config["seed"],
        )
        rows.append(row)
    frame = pd.DataFrame(rows)
    curves = []
    for order in config["orders"]:
        name = {2: "BPSK", 4: "QPSK", 16: "16-QAM", 64: "64-QAM"}[order]
        for db in np.linspace(min(config["ebn0_db"]), max(config["ebn0_db"]), 161):
            curves.append(
                {
                    "modulation": name,
                    "ebn0_db": float(db),
                    "ber_theory_exact": ber_awgn(db, order),
                    "ser_theory_exact": ser_awgn(db, order),
                    "ber_qam_approx": qam_ber_nearest_neighbor(db, order)
                    if order in (16, 64)
                    else None,
                }
            )
    theoretical = pd.DataFrame(curves)
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    # Les listes sont sérialisées explicitement en JSON dans la colonne CSV.
    export = frame.copy()
    export["errors_per_bit_position"] = export["errors_per_bit_position"].map(json.dumps)
    export.to_csv(ROOT / "results/datasets/ber_comparison.csv", index=False)
    theoretical.to_csv(ROOT / "results/datasets/awgn_theory.csv", index=False)
    (ROOT / "results/reports/ber_comparison.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for metric in ["ber", "ser"]:
        plot_error_curves(
            frame, theoretical, metric, ROOT / f"results/figures/06_{metric}_comparison.png"
        )
    plot_qam_approximation(theoretical, ROOT / "results/figures/06_qam_approximation.png")
    summary = {
        "n_points": len(rows),
        "total_bits": int(frame["n_bits"].sum()),
        "points_zero_bit_errors": int((frame["bit_errors"] == 0).sum()),
        "ber_theory_in_95_ci": int(
            (
                (frame.ber_theory_exact >= frame.ber_ci_lower)
                & (frame.ber_theory_exact <= frame.ber_ci_upper)
            ).sum()
        ),
        "ser_theory_in_95_ci": int(
            (
                (frame.ser_theory_exact >= frame.ser_ci_lower)
                & (frame.ser_theory_exact <= frame.ser_ci_upper)
            ).sum()
        ),
        "all_ber_validation_passed": bool(frame.ber_theory_in_validation_interval.all()),
        "all_ser_validation_passed": bool(frame.ser_theory_in_validation_interval.all()),
        "familywise_confidence_at_least": 0.99,
        "numpy_version": np.__version__,
    }
    (ROOT / "results/reports/ber_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    print(
        frame[
            ["modulation", "ebn0_db", "n_bits", "bit_errors", "ber", "ber_theory_exact"]
        ].to_string(index=False)
    )
    if not summary["all_ber_validation_passed"] or not summary["all_ser_validation_passed"]:
        raise RuntimeError(
            "Comparaison théorique hors enveloppe de validation ; investiguer avant progression."
        )


if __name__ == "__main__":
    run()
