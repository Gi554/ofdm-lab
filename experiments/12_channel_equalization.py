"""Comparer les décisions et MSE sur un même burst, à canal parfaitement connu."""

import json

import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.channels import channel_memory
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.metrics import mean_binomial_interval
from ofdm_lab.multipath_simulation import simulate_known_channel
from ofdm_lab.visualization import plot_equalization_results


def run():
    params, fixed, fading = load_channels()
    options = json.loads((ROOT / "configs/equalization.json").read_text(encoding="utf-8"))
    channels = {"fixed": fixed, "rayleigh_static": fading}
    cases = [
        (name, m, cp, db)
        for name in channels
        for m in options["orders"]
        for cp in options["cp_lengths"]
        for db in options["ebn0_db"]
    ]
    seeds = np.random.SeedSequence(options["seed"] + 3).spawn(len(cases))
    comparisons = sum(cp >= channel_memory(channels[name]) for name, _, cp, _ in cases) * 4
    validation_confidence = 1 - 0.01 / comparisons
    rows = []
    bits_transmitted = 0
    paired = True
    for (name, order, cp, db), seed in zip(cases, seeds, strict=True):
        config = OFDMConfig(params["n_fft"], params["n_active"], cp, order, params["spacing_hz"])
        measurements = simulate_known_channel(
            config,
            channels[name],
            db,
            options["n_ofdm_symbols"],
            int(seed.generate_state(1)[0]),
            options["energy_reference"],
        )
        paired = paired and measurements[1]["bit_errors"] == measurements[2]["bit_errors"]
        bits_transmitted += measurements[0]["n_bits"]
        for row in measurements:
            row.update(
                channel=name,
                root_seed=options["seed"] + 3,
                ber_validation_passed=None,
                ser_validation_passed=None,
            )
            if row["ber_theory_conditional"] is not None:
                bl, bh = mean_binomial_interval(
                    np.asarray(row["errors_by_carrier_bit"]).ravel(),
                    row["n_ofdm_symbols"],
                    validation_confidence,
                )
                sl, sh = mean_binomial_interval(
                    row["errors_by_carrier"], row["n_ofdm_symbols"], validation_confidence
                )
                row.update(
                    ber_validation_lower=bl,
                    ber_validation_upper=bh,
                    ser_validation_lower=sl,
                    ser_validation_upper=sh,
                    validation_confidence_per_point=validation_confidence,
                    ber_validation_passed=bl <= row["ber_theory_conditional"] <= bh,
                    ser_validation_passed=sl <= row["ser_theory_conditional"] <= sh,
                )
            rows.append(row)
    ideal = []
    for name, h in channels.items():
        for order in options["orders"]:
            for cp in options["cp_lengths"]:
                config = OFDMConfig(
                    params["n_fft"], params["n_active"], cp, order, params["spacing_hz"]
                )
                for row in simulate_known_channel(config, h, None, 100, options["seed"]):
                    ideal.append(
                        {
                            "channel": name,
                            "order": order,
                            "cp_length": cp,
                            "cp_sufficient": row["cp_sufficient"],
                            "method": row["method"],
                            "n_bits": row["n_bits"],
                            "bit_errors": row["bit_errors"],
                            "mse": row["mse"],
                        }
                    )
    frame = pd.DataFrame(rows)
    for folder in ["figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    export = frame.copy()
    for column in ["errors_by_carrier_bit", "errors_by_carrier", "channel_taps"]:
        export[column] = export[column].map(json.dumps)
    export.to_csv(ROOT / "results/datasets/equalization.csv", index=False)
    # Une mesure complète par ligne : les tableaux de compteurs restent lisibles séparément.
    (ROOT / "results/reports/equalization.json").write_text(
        "[\n" + ",\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n]\n",
        encoding="utf-8",
    )
    all_ber = all(
        row["ber_validation_passed"] for row in rows if row["ber_validation_passed"] is not None
    )
    all_ser = all(
        row["ser_validation_passed"] for row in rows if row["ser_validation_passed"] is not None
    )
    sufficient_ideal = [r for r in ideal if r["cp_sufficient"] and r["method"] != "none"]
    summary = {
        "n_channel_trials": len(cases),
        "n_measurements": len(rows),
        "unique_transmitted_bits": bits_transmitted,
        "bit_decisions_all_methods": int(frame.n_bits.sum()),
        "zf_mmse_gain_aware_identical_error_counts": paired,
        "all_conditional_ber_validation_passed": all_ber,
        "all_conditional_ser_validation_passed": all_ser,
        "conditional_comparisons": comparisons,
        "familywise_confidence_at_least": 0.99,
        "all_noiseless_sufficient_cp_equalized_passed": all(
            r["bit_errors"] == 0 for r in sufficient_ideal
        ),
        "noiseless_cases": ideal,
        "numpy_version": np.__version__,
    }
    (ROOT / "results/reports/equalization_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    plot_equalization_results(frame, ROOT / "results/figures/12_channel_equalization.png")
    print(json.dumps({k: v for k, v in summary.items() if k != "noiseless_cases"}, indent=2))
    print(
        frame[(frame.order == 16) & (frame.cp_length == 16) & (frame.ebn0_db == 12)][
            ["channel", "method", "n_bits", "bit_errors", "ber", "mse", "mse_theory_conditional"]
        ].to_string(index=False)
    )
    if not all([paired, all_ber, all_ser, summary["all_noiseless_sufficient_cp_equalized_passed"]]):
        raise RuntimeError("Validation d'égalisation échouée ; investiguer avant phase suivante.")


if __name__ == "__main__":
    run()
