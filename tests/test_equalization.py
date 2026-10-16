"""Validation des poids, biais, singularités, MSE et décisions des égaliseurs."""

import numpy as np
import pytest

from ofdm_lab import demodulate_qam, generate_bits, modulate_qam
from ofdm_lab.equalization import decision_symbols, equalize
from ofdm_lab.noise import add_awgn


def test_exact_zf_and_mmse_weights_and_gain():
    h = np.array([0.2 + 0.1j, 1 - 1j])
    x = np.array([1 + 1j, -1 + 1j])
    n0 = 0.3
    zf = equalize(h * x, h, "zf", n0)
    mmse = equalize(h * x, h, "mmse", n0)
    np.testing.assert_allclose(zf.symbols, x)
    np.testing.assert_allclose(zf.decision_gain, 1)
    np.testing.assert_allclose(zf.noise_variance_out, n0 / abs(h) ** 2)
    np.testing.assert_allclose(mmse.weights, h.conj() / (abs(h) ** 2 + n0))
    np.testing.assert_allclose(mmse.symbols, mmse.decision_gain * x)
    np.testing.assert_allclose(decision_symbols(mmse), x)


def test_mmse_lowers_estimation_mse_but_gain_aware_decisions_match_zf():
    bits = generate_bits(200000, 42)
    x = modulate_qam(bits, 16)
    h = np.resize(np.array([0.08 + 0.02j, 0.5 - 0.4j, 1.2 + 0.3j]), x.size)
    n0 = 0.2
    y = add_awgn(h * x, n0, 43)
    zf = equalize(y, h, "zf", n0)
    mmse = equalize(y, h, "mmse", n0)
    assert np.mean(abs(mmse.symbols - x) ** 2) < np.mean(abs(zf.symbols - x) ** 2)
    np.testing.assert_array_equal(
        demodulate_qam(decision_symbols(zf), 16), demodulate_qam(decision_symbols(mmse), 16)
    )


def test_null_channel_is_not_silently_inverted():
    with pytest.raises(ValueError):
        equalize([1, 2], [1, 0], "zf", 0.1)
    mmse = equalize([1, 2], [1, 0], "mmse", 0.1)
    assert mmse.erasures[1]
    np.testing.assert_allclose(mmse.symbols[1], 0)
    np.testing.assert_allclose(decision_symbols(mmse)[1], 0)
    assert not np.any(np.isnan(mmse.symbols))


def test_broadcasting_preserves_received_dimensions():
    result = equalize(np.ones((3, 4)), np.arange(1, 5), "zf", 0.1)
    assert result.symbols.shape == (3, 4)
    with pytest.raises(ValueError):
        equalize(np.ones((1, 4)), np.ones((4, 1)))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"noise_variance": -1},
        {"noise_variance": np.nan},
        {"symbol_energy": 0},
        {"minimum_magnitude": -1},
        {"method": "unknown"},
    ],
)
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        equalize([1], [1], **kwargs)


def test_no_noise_mmse_equals_zf_for_nonzero_channel():
    h = np.array([0.2j, 0.8])
    y = np.array([1 + 1j, 2j])
    np.testing.assert_allclose(equalize(y, h, "mmse", 0).symbols, equalize(y, h, "zf").symbols)
