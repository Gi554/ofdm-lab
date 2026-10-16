"""Allocation, CP, dimensions et restitution idéale avec références indépendantes."""

import numpy as np
import pytest

from ofdm_lab import generate_bits
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.receiver import receive, remove_cyclic_prefix
from ofdm_lab.transmitter import add_cyclic_prefix, transmit


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("cp", [0, 16, 64])
def test_ideal_roundtrip_and_energy(order, cp):
    config = OFDMConfig(order=order, cp_length=cp)
    bits = generate_bits(10 * config.bits_per_ofdm_symbol, 42)
    tx = transmit(bits, config)
    rx = receive(tx.waveform, config)
    np.testing.assert_array_equal(rx.bits, bits)
    np.testing.assert_allclose(rx.symbols, tx.grid[:, config.active_indices].ravel(), atol=2e-14)
    assert tx.grid.shape == tx.useful.shape == (10, 64)
    assert tx.with_cp.shape == (10, 64 + cp)
    assert tx.waveform.size == 10 * (64 + cp)
    np.testing.assert_allclose(np.sum(abs(tx.useful) ** 2), np.sum(abs(tx.grid) ** 2), rtol=1e-13)
    nulls = np.setdiff1d(np.arange(64), config.active_indices)
    np.testing.assert_array_equal(tx.grid[:, nulls], 0)
    assert 0 in nulls and 32 in nulls


def test_allocation_order_and_known_tone():
    config = OFDMConfig(n_fft=8, n_active=4, cp_length=0, order=2)
    np.testing.assert_array_equal(config.active_indices, [6, 7, 1, 2])
    tx = transmit([0, 1, 0, 1], config)
    expected = np.zeros(8, dtype=complex)
    expected[[6, 7, 1, 2]] = [1, -1, 1, -1]
    n = np.arange(8)
    manual = np.sum(
        expected[None, :] * np.exp(2j * np.pi * n[:, None] * n[None, :] / 8), axis=1
    ) / np.sqrt(8)
    np.testing.assert_allclose(tx.waveform, manual, atol=1e-14)


@pytest.mark.parametrize("cp", [0, 1, 4])
def test_prefix_exact_copy_and_removal(cp):
    x = np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=complex)
    prefixed = add_cyclic_prefix(x, cp)
    np.testing.assert_array_equal(remove_cyclic_prefix(prefixed, cp), x)
    if cp:
        np.testing.assert_array_equal(prefixed[:, :cp], x[:, -cp:])
    assert prefixed.shape == (2, 4 + cp)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_fft": 63},
        {"n_active": 53},
        {"n_active": 64},
        {"cp_length": -1},
        {"cp_length": 65},
        {"cp_length": True},
        {"order": 8},
        {"spacing_hz": 0},
    ],
)
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        OFDMConfig(**kwargs)


def test_incomplete_frames_and_invalid_cp():
    config = OFDMConfig()
    for bits in [[], [0, 1]]:
        with pytest.raises(ValueError):
            transmit(bits, config)
    for values in [[], [0], np.zeros((1, 80)), [np.nan] * 80]:
        with pytest.raises(ValueError):
            receive(values, config)
    for cp in [-1, 5, True]:
        with pytest.raises(ValueError):
            add_cyclic_prefix([1, 2, 3, 4], cp)


def test_unsigned_numpy_configuration_is_canonicalized():
    config = OFDMConfig(n_fft=np.uint64(64), n_active=np.uint64(52), cp_length=np.uint64(16))
    assert type(config.n_fft) is type(config.n_active) is int
    np.testing.assert_array_equal(config.active_indices[:2], [38, 39])
