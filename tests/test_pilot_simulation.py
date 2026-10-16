import numpy as np
import pytest

from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout
from ofdm_lab.pilot_simulation import simulate_pilot_channel


def test_reproducible_trials_and_data_counters():
    layout = PilotLayout(OFDMConfig(order=16), 4)
    a = simulate_pilot_channel(layout, [1], 18, 300, 42)
    b = simulate_pilot_channel(layout, [1], 18, 300, 42)
    assert a == b
    assert len(a) == 3
    assert a[0]["bit_errors"] == a[1]["bit_errors"]
    for row in a:
        assert row["n_bits"] == 300 * layout.bits_per_frame
        assert row["ber_ci_lower"] <= row["ber"] <= row["ber_ci_upper"]
    row = a[2]
    assert row["interpolation_bias_mse"] < 1e-28
    assert abs(row["channel_mse_data"] - row["channel_mse_theory"]) < 6 * np.sqrt(
        row["channel_mse_mean_variance"]
    )


def test_insufficient_prefix_rejected():
    with pytest.raises(ValueError):
        simulate_pilot_channel(PilotLayout(OFDMConfig(cp_length=0)), [1, 0.2], 12, 10, 42)
