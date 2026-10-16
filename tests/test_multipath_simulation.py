"""Validation conditionnelle stratifiée des essais multitrajets appariés."""

import numpy as np

from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.multipath_simulation import simulate_known_channel


def test_noiseless_channel_and_cp_condition():
    h = np.array([1, 0, 0, 0, -0.8j])
    config = OFDMConfig(cp_length=4, order=16)
    rows = simulate_known_channel(config, h, None, 30, 42)
    for row in rows[1:]:
        assert row["bit_errors"] == 0
        assert row["mse"] < 1e-25
    short = simulate_known_channel(OFDMConfig(cp_length=0, order=16), h, None, 30, 42)
    for row in short:
        assert row["ber_ci_lower"] is row["ber_ci_upper"] is None
        assert row["mse_theory_conditional"] is None
    assert short[1]["mse"] > 1e-4


def test_paired_decisions_and_conditional_theory():
    h = np.array([1, 0, 0, 0.5j])
    rows = simulate_known_channel(OFDMConfig(order=16), h, 6, 600, 43, confidence=1 - 1e-7)
    zf, mmse = rows[1:3]
    assert zf["bit_errors"] == mmse["bit_errors"]
    assert mmse["mse"] < zf["mse"]
    for row in [zf, mmse]:
        assert row["ber_ci_lower"] <= row["ber_theory_conditional"] <= row["ber_ci_upper"]
        assert row["ser_ci_lower"] <= row["ser_theory_conditional"] <= row["ser_ci_upper"]
    assert rows == simulate_known_channel(OFDMConfig(order=16), h, 6, 600, 43, confidence=1 - 1e-7)
