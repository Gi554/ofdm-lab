"""Validation exhaustive des alphabets QAM Gray et décisions géométriques."""

import numpy as np
import pytest

from ofdm_lab import demodulate_qam, generate_bits, modulate_qam

ORDERS = [16]


def alphabet(order):
    k = order.bit_length() - 1
    return ((np.arange(order)[:, None] >> np.arange(k - 1, -1, -1)) & 1).astype(np.uint8)


@pytest.mark.parametrize("order", ORDERS)
def test_exhaustive_alphabet(order):
    labels = alphabet(order)
    symbols = modulate_qam(labels.ravel(), order)
    np.testing.assert_array_equal(demodulate_qam(symbols, order), labels.ravel())
    assert np.unique(symbols).size == order
    assert symbols.shape == (order,)
    assert symbols.dtype == np.complex128
    assert demodulate_qam(symbols, order).dtype == np.uint8
    np.testing.assert_allclose(np.mean(abs(symbols) ** 2), 1, atol=1e-14)
    np.testing.assert_allclose(np.mean(symbols), 0, atol=1e-14)
    assert modulate_qam([], order).size == demodulate_qam([], order).size == 0


@pytest.mark.parametrize("order", ORDERS)
def test_all_horizontal_vertical_neighbors_are_gray(order):
    labels = alphabet(order)
    symbols = modulate_qam(labels.ravel(), order)
    expected_distance = np.sqrt(6 / (order - 1))
    distances = abs(symbols[:, None] - symbols[None, :])
    neighbors = np.isclose(distances, expected_distance, rtol=1e-12, atol=1e-12)
    hamming = np.count_nonzero(labels[:, None, :] != labels[None, :, :], axis=2)
    assert np.all(hamming[neighbors] == 1)
    levels = int(np.sqrt(order))
    assert np.count_nonzero(neighbors) == 4 * levels * (levels - 1)
    np.testing.assert_allclose(np.min(distances[distances > 0]), expected_distance)


@pytest.mark.parametrize("order", ORDERS)
def test_roundtrip_random_and_interior_perturbation(order):
    k = order.bit_length() - 1
    bits = generate_bits(25000 * k, 123)
    symbols = modulate_qam(bits, order)
    # Décalage déterministe plus petit que la demi-distance entre deux niveaux.
    offset = 0.49 * np.sqrt(6 / (order - 1)) * (1 + 1j)
    np.testing.assert_array_equal(demodulate_qam(symbols + offset, order), bits)


@pytest.mark.parametrize("order", ORDERS)
def test_decisions_match_independent_euclidean_reference(order):
    labels = alphabet(order)
    points = modulate_qam(labels.ravel(), order)
    rng = np.random.default_rng(94)
    samples = rng.uniform(-3, 3, 1000) + 1j * rng.uniform(-3, 3, 1000)
    closest = np.argmin(abs(samples[:, None] - points[None, :]), axis=1)
    np.testing.assert_array_equal(demodulate_qam(samples, order), labels[closest].ravel())


def test_known_16qam_axis_mapping():
    labels = np.array([[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0]])
    np.testing.assert_allclose(
        modulate_qam(labels.ravel(), 16), (np.array([3, 1, -1, -3]) + 3j) / np.sqrt(10)
    )
    # I=Q=0 est à égalité entre quatre points : décision vers +1 sur chaque axe.
    np.testing.assert_array_equal(demodulate_qam([0j], 16), [0, 1, 0, 1])


@pytest.mark.parametrize("order", ORDERS)
def test_qam_length_and_invalid_bits(order):
    with pytest.raises(ValueError):
        modulate_qam([0], order)
    for bits in [[2], [0.5], [np.nan], [[0, 1]], [1j], ["0"]]:
        with pytest.raises(ValueError):
            modulate_qam(bits, order)
    for symbols in [[np.inf], [np.nan], [[0j]]]:
        with pytest.raises(ValueError):
            demodulate_qam(symbols, order)


@pytest.mark.parametrize("order", [True, 16.0, "16", 4, 32, -16])
def test_invalid_qam_orders(order):
    with pytest.raises(ValueError):
        modulate_qam([], order)
    with pytest.raises(ValueError):
        demodulate_qam([], order)
