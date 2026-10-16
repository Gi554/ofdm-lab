"""Bilan CP, variance FFT et cohérence statistique du récepteur OFDM sur AWGN."""

import numpy as np
import pytest

from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.noise import add_awgn
from ofdm_lab.ofdm_simulation import energy_budget, simulate_ofdm_awgn
from ofdm_lab.receiver import receive


def test_energy_budget_cp_penalty_and_active_fraction():
    config = OFDMConfig()
    useful = energy_budget(config, 0, "useful")
    total = energy_budget(config, 0, "total")
    np.testing.assert_allclose(
        [useful["expected_useful_energy"], useful["expected_cp_energy"]], [52, 13]
    )
    np.testing.assert_allclose(total["noise_variance"] / useful["noise_variance"], 1.25)
    np.testing.assert_allclose(total["effective_useful_ebn0_db"], -10 * np.log10(1.25))
    np.testing.assert_allclose(useful["expected_sample_power"], 52 / 64)
    np.testing.assert_allclose(useful["payload_rate_bps"], 1248000)
    with pytest.raises(ValueError):
        energy_budget(config, 0, "unknown")


def test_fft_keeps_noise_variance_on_active_carriers():
    config = OFDMConfig()
    size = 2000 * (config.n_fft + config.cp_length)
    received = receive(add_awgn(np.zeros(size), 0.4, 42), config).symbols
    np.testing.assert_allclose(
        np.mean(abs(received) ** 2), 0.4, atol=6 * 0.4 / np.sqrt(received.size), rtol=0
    )
    assert abs(np.mean(received[1:] * received[:-1].conj())) < 6 * 0.4 / np.sqrt(received.size)


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("reference", ["useful", "total"])
def test_ofdm_ber_ser_match_effective_theory(order, reference):
    result = simulate_ofdm_awgn(
        OFDMConfig(order=order), 6, 1000, 100 + order, reference=reference, confidence=1 - 1e-7
    )
    assert result["ber_ci_lower"] <= result["ber_theory_exact"] <= result["ber_ci_upper"]
    assert result["ser_ci_lower"] <= result["ser_theory_exact"] <= result["ser_ci_upper"]
    assert result["n_bits"] == 1000 * 52 * (order.bit_length() - 1)


def test_reproducible_other_fft_and_partial_block():
    config = OFDMConfig(n_fft=128, n_active=100, cp_length=0, order=16)
    result = simulate_ofdm_awgn(config, 4, 33, 42, batch_frames=16)
    assert result == simulate_ofdm_awgn(config, 4, 33, 42, batch_frames=16)
    with pytest.raises(ValueError):
        simulate_ofdm_awgn(config, 4, 0, 42)
