"""Validation Monte-Carlo avec tolérances statistiques adaptées et effectifs fixes."""

import numpy as np
import pytest

from ofdm_lab.simulation import simulate_awgn


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("ebn0", [0, 6])
def test_simulation_agrees_with_exact_theory(order, ebn0):
    # Niveau très conservateur pour rendre la validation non fragile entre plateformes.
    result = simulate_awgn(order, ebn0, 240000, seed=200 + order + ebn0, confidence=1 - 1e-7)
    assert result["ber_ci_lower"] <= result["ber_theory_exact"] <= result["ber_ci_upper"]
    assert result["ser_ci_lower"] <= result["ser_theory_exact"] <= result["ser_ci_upper"]
    assert sum(result["errors_per_bit_position"]) == result["bit_errors"]
    assert result["symbol_errors"] <= result["bit_errors"]
    assert result["n_bits"] == 240000


def test_reproducible_partial_last_block_and_zero_error_bound():
    first = simulate_awgn(16, 30, 12000, 42, batch_symbols=71)
    assert first == simulate_awgn(16, 30, 12000, 42, batch_symbols=71)
    assert first["n_symbols"] == 3000
    assert first["bit_errors"] == first["symbol_errors"] == 0
    assert first["ber_ci_upper"] > 0
    np.testing.assert_allclose(first["zero_symbol_error_upper_one_sided"], 1 - 0.05 ** (1 / 3000))


@pytest.mark.parametrize("count", [0, -1, 1.5, True, 5])
def test_invalid_counts(count):
    with pytest.raises(ValueError):
        simulate_awgn(16, 0, count, 42)


def test_invalid_confidence_and_block():
    with pytest.raises(ValueError):
        simulate_awgn(16, 0, 120, 42, confidence=1)
    with pytest.raises(ValueError):
        simulate_awgn(16, 0, 120, 42, batch_symbols=0)
