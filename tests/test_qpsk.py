"""Validation de la fonctionnalité scientifique associée."""

import numpy as np
import pytest

from ofdm_lab import demodulate_qpsk, generate_bits, modulate_qpsk


@pytest.mark.parametrize("mod,demod", [(modulate_qpsk, demodulate_qpsk)])
def test_roundtrip(mod, demod):
    bits = generate_bits(100000, 123)
    np.testing.assert_array_equal(demod(mod(bits)), bits)
    np.testing.assert_allclose(np.mean(np.abs(mod(bits)) ** 2), 1, atol=1e-14)
    assert mod(bits).dtype == np.complex128
    assert mod([]).size == demod([]).size == 0


def test_qpsk_gray_mapping_and_neighbors():
    bits = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
    symbols = modulate_qpsk(bits.ravel())
    np.testing.assert_allclose(symbols, np.array([1 + 1j, 1 - 1j, -1 - 1j, -1 + 1j]) / np.sqrt(2))
    assert np.all(np.count_nonzero(bits != np.roll(bits, 1, axis=0), axis=1) == 1)
    np.testing.assert_allclose(np.abs(symbols - np.roll(symbols, 1)), np.sqrt(2))
    assert modulate_qpsk(bits.ravel()).shape == (4,)
    np.testing.assert_array_equal(demodulate_qpsk([0j]), [0, 0])


@pytest.mark.parametrize("bits", [[2], [-1], [0.5], [np.nan], [[0, 1]], [1j], ["0"]])
@pytest.mark.parametrize("mod", [modulate_qpsk])
def test_invalid_bits(bits, mod):
    with pytest.raises(ValueError):
        mod(bits)


@pytest.mark.parametrize("symbols", [[np.nan], [np.inf], [[1, 2]]])
@pytest.mark.parametrize("demod", [demodulate_qpsk])
def test_invalid_symbols(symbols, demod):
    with pytest.raises(ValueError):
        demod(symbols)


def test_odd_qpsk():
    with pytest.raises(ValueError):
        modulate_qpsk([0, 1, 0])


def test_nonideal_symbols_inside_decision_regions():
    np.testing.assert_array_equal(demodulate_qpsk([0.1 - 0.3j, -2 + 0.4j]), [0, 1, 1, 0])
