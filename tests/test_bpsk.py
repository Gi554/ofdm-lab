"""Validation de la fonctionnalité scientifique associée."""

import numpy as np
import pytest

from ofdm_lab import demodulate_bpsk, generate_bits, modulate_bpsk


@pytest.mark.parametrize("mod,demod", [(modulate_bpsk, demodulate_bpsk)])
def test_roundtrip(mod, demod):
    bits = generate_bits(100000, 123)
    np.testing.assert_array_equal(demod(mod(bits)), bits)
    np.testing.assert_allclose(np.mean(np.abs(mod(bits)) ** 2), 1, atol=1e-14)
    assert mod(bits).dtype == np.complex128
    assert mod([]).size == demod([]).size == 0


def test_bpsk_mapping():
    np.testing.assert_allclose(modulate_bpsk([0, 1]), [1, -1])
    np.testing.assert_array_equal(demodulate_bpsk([0, -0.1, 0.1]), [0, 1, 0])


@pytest.mark.parametrize("bits", [[2], [-1], [0.5], [np.nan], [[0, 1]], [1j], ["0"]])
@pytest.mark.parametrize("mod", [modulate_bpsk])
def test_invalid_bits(bits, mod):
    with pytest.raises(ValueError):
        mod(bits)


@pytest.mark.parametrize("symbols", [[np.nan], [np.inf], [[1, 2]]])
@pytest.mark.parametrize("demod", [demodulate_bpsk])
def test_invalid_symbols(symbols, demod):
    with pytest.raises(ValueError):
        demod(symbols)


def test_nonideal_symbols_inside_decision_regions():
    np.testing.assert_array_equal(demodulate_bpsk([0.2 + 3j, -0.4 - 2j]), [0, 1])
