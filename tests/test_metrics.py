"""Compteurs et couverture des intervalles, y compris bits QAM corrélés."""

import numpy as np
import pytest
from scipy.stats import binomtest

from ofdm_lab.metrics import ber_interval, binomial_interval, count_errors, zero_error_upper_bound


def test_known_bit_and_symbol_counts():
    counts = count_errors([0, 0, 0, 0, 1, 1, 0, 1], [0, 1, 1, 0, 1, 1, 0, 1], 2)
    assert (counts.n_bits, counts.n_symbols, counts.bit_errors, counts.symbol_errors) == (
        8,
        4,
        2,
        2,
    )
    assert counts.per_bit_position == (1, 1)
    np.testing.assert_allclose([counts.ber, counts.ser], [0.25, 0.5])


@pytest.mark.parametrize(
    "tx,rx,k",
    [([], [], 1), ([0], [0, 1], 1), ([0, 1, 0], [0, 1, 0], 2), ([2], [0], 1), ([0], [0], 0)],
)
def test_invalid_comparisons(tx, rx, k):
    with pytest.raises(ValueError):
        count_errors(tx, rx, k)


@pytest.mark.parametrize("errors,trials", [(0, 100), (10, 10), (5, 10), (123, 1000)])
def test_exact_interval_matches_scipy_binomtest(errors, trials):
    reference = binomtest(errors, trials).proportion_ci(confidence_level=0.95, method="exact")
    np.testing.assert_allclose(binomial_interval(errors, trials), reference, atol=1e-12)


def test_zero_errors_is_not_zero_probability():
    low, high = binomial_interval(0, 1000)
    assert low == 0 and high > 0
    np.testing.assert_allclose(high, 1 - 0.025 ** (1 / 1000))
    np.testing.assert_allclose(zero_error_upper_bound(1000), 1 - 0.05 ** (1 / 1000))
    assert zero_error_upper_bound(10000) < zero_error_upper_bound(1000)


def test_ber_interval_handles_perfectly_correlated_bit_positions():
    single = binomial_interval(20, 100)
    joint = ber_interval([20, 20], 100)
    assert joint[0] < single[0] < 0.2 < single[1] < joint[1]
    np.testing.assert_allclose(ber_interval([20], 100), single)
    # Les essais indépendants sont des symboles ; ne pas diviser par deux cette borne.
    np.testing.assert_allclose(ber_interval([0, 0], 100)[1], 1 - (0.05 / 4) ** 0.01)


@pytest.mark.parametrize(
    "errors,trials,confidence",
    [
        (-1, 10, 0.95),
        (11, 10, 0.95),
        (True, 10, 0.95),
        (1.0, 10, 0.95),
        (0, 0, 0.95),
        (0, 10, 0),
        (0, 10, 1),
        (0, 10, np.nan),
    ],
)
def test_invalid_binomial_inputs(errors, trials, confidence):
    with pytest.raises(ValueError):
        binomial_interval(errors, trials, confidence)


@pytest.mark.parametrize("counts", [[], [[0]], [1.5], [-1], [11]])
def test_invalid_position_counts(counts):
    with pytest.raises(ValueError):
        ber_interval(counts, 10)
