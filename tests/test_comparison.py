import pytest

from ofdm_lab.comparison import simulate_comparison
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout


@pytest.mark.parametrize("n_fft,n_active", [(64, 52), (128, 104)])
@pytest.mark.parametrize("order", [2, 4, 16, 64])
def test_comparison_pairs_resources_and_gain_decisions(n_fft, n_active, order):
    layout = PilotLayout(OFDMConfig(n_fft, n_active, 16, order, 960000 / n_fft), 4)
    rows = simulate_comparison(layout, [1, 0, 0.25j], 12, 50, 42)
    assert len(rows) == 5
    assert rows[1]["errors_by_carrier_bit"] == rows[2]["errors_by_carrier_bit"]
    assert rows[3]["errors_by_carrier_bit"] == rows[4]["errors_by_carrier_bit"]
    for row in rows:
        assert row["sample_rate_hz"] == 960000
        assert row["n_bits"] == 50 * layout.bits_per_frame
        assert row["noise_variance"] == rows[0]["noise_variance"]
        assert row["ber_ci_lower"] <= row["ber"] <= row["ber_ci_upper"]
    assert rows[1]["channel_mse_data"] == 0
    assert rows[3]["channel_mse_data"] == rows[4]["channel_mse_data"]


def test_short_prefix_omits_invalid_model_and_intervals():
    layout = PilotLayout(OFDMConfig(cp_length=0, order=16), 4)
    rows = simulate_comparison(layout, [1, 0, 0, -0.8], 18, 40, 4)
    for row in rows:
        assert not row["cp_sufficient"]
        assert row["ber_ci_lower"] is None
        assert row["confidence"] is None
        assert row["ber_theory_conditional"] is None
    assert rows[1]["bit_errors"] > 0


def test_flat_known_channel_matches_uncorrected_and_reproduces():
    layout = PilotLayout(OFDMConfig(order=4), 8)
    a = simulate_comparison(layout, [1], 6, 80, 9)
    assert a == simulate_comparison(layout, [1], 6, 80, 9)
    assert a[0]["bit_errors"] == a[1]["bit_errors"]
    assert a[1]["ber_theory_conditional"] is not None
    assert a[1]["symbol_mse"] >= a[2]["symbol_mse"]
