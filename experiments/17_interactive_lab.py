"""Vérification reproductible des services utilisés par le laboratoire Streamlit."""

import json
from dataclasses import replace
from pathlib import Path

from ofdm_lab.image_transport import load_image
from ofdm_lab.laboratory import LabSettings, csv_bytes, run_image_lab, run_lab, run_sweep

ROOT = Path(__file__).resolve().parents[1]


def run():
    settings = LabSettings()
    result = run_lab(settings)
    sweep = run_sweep(replace(settings, frames=16), [6, 18])
    short = run_lab(replace(settings, channel="Multitrajet à creux", cp_length=0, frames=16))
    image = run_image_lab(
        replace(settings, channel="AWGN", ebn0_db=30), load_image(ROOT / "assets/test_pattern.png")
    )
    checks = dict(
        default_parameters_preserved=result["settings"]["seed"] == settings.seed,
        five_paired_methods=len(result["rows"]) == 5,
        bounded_trace=len(result["trace"]["waveform"]) <= 8192,
        sweep_points=len(sweep["rows"]) == 10 and sweep["levels"] == [6.0, 18.0],
        short_cp_has_no_binomial_interval=short["selected"]["ber_ci_lower"] is None,
        image_complete_crc_valid=image["trial"].reception.image_crc_valid is True,
    )
    summary = dict(
        checks=checks,
        all_checks_passed=all(checks.values()),
        default_settings=result["settings"],
        default_measurement=result["selected"],
        sweep_settings=sweep["settings"],
        sweep_levels_db=sweep["levels"],
        image_measurement=image["trial"].metrics,
        ui_tests="Streamlit AppTest scenarios are run separately by pytest",
        deployment="local Streamlit; no remote hosting configured",
    )
    (ROOT / "results/reports/interactive_lab.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "results/datasets/interactive_sweep.csv").write_bytes(csv_bytes(sweep["rows"]))
    print(json.dumps(checks, indent=2))
    if not summary["all_checks_passed"]:
        raise RuntimeError("Échec de validation des services interactifs.")


if __name__ == "__main__":
    run()
