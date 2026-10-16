"""Convolution indépendante, causalité, normalisation FFT et loi Rayleigh."""

import numpy as np
import pytest

from ofdm_lab import generate_bits
from ofdm_lab.channels import apply_multipath, channel_memory, frequency_response, rayleigh_channel
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.receiver import receive
from ofdm_lab.transmitter import transmit


def test_known_linear_convolution_and_tail():
    np.testing.assert_allclose(apply_multipath([1, 2, 3], [1, 0.5]), [1, 2.5, 4, 1.5])
    np.testing.assert_allclose(apply_multipath([0, 1, 0], [0, 0, 2j]), [0, 0, 0, 2j, 0])
    assert channel_memory([1, 0, 0.5, 0, 0]) == 2
    np.testing.assert_allclose(frequency_response([2], 8), 2)
    n = np.arange(8)
    np.testing.assert_allclose(
        frequency_response([1, 0, 0.5j], 8), 1 + 0.5j * np.exp(-2j * np.pi * n * 2 / 8)
    )


@pytest.mark.parametrize("cp", [0, 3, 4, 16])
def test_cp_controls_circular_convolution_identity(cp):
    config = OFDMConfig(cp_length=cp, order=16)
    bits = generate_bits(20 * config.bits_per_ofdm_symbol, 42)
    tx = transmit(bits, config)
    h = np.array([1, 0, 0, 0, 0.8j])
    stream = apply_multipath(tx.waveform, h)
    assert stream.size == tx.waveform.size + 4
    grid = receive(stream[: tx.waveform.size], config).grid
    target = tx.grid * frequency_response(h, 64)
    if cp >= 4:
        np.testing.assert_allclose(grid, target, atol=3e-14)
    else:
        assert np.mean(abs(grid - target) ** 2) > 1e-4


def test_rayleigh_reproducibility_and_expected_energy():
    p = np.array([0.7, 0.2, 0.1])
    samples = np.array([rayleigh_channel([0, 2, 5], p, seed) for seed in range(4000)])
    np.testing.assert_array_equal(samples[42], rayleigh_channel([0, 2, 5], p, 42))
    np.testing.assert_allclose(
        np.mean(abs(samples) ** 2, axis=0)[[0, 2, 5]], p, atol=6 * p.max() / np.sqrt(4000), rtol=0
    )
    energy = np.sum(abs(samples) ** 2, axis=1)
    assert abs(energy.mean() - 1) < 6 * np.sqrt(np.sum(p * p) / 4000)
    assert energy.std() > 0.1  # Ne jamais normaliser chaque réalisation à une énergie 1.
    np.testing.assert_array_equal(samples[:, [1, 3, 4]], 0)


@pytest.mark.parametrize("bad", [[], [0, 0], [np.nan], [[1, 2]]])
def test_invalid_taps(bad):
    with pytest.raises(ValueError):
        apply_multipath([1, 2], bad)


@pytest.mark.parametrize(
    "delays,powers",
    [
        ([0, 0], [1, 1]),
        ([-1], [1]),
        ([0.5], [1]),
        ([True], [1]),
        ([0], [0]),
        ([0], [-1]),
        ([0], [np.nan]),
        ([0], [1j]),
        ([0], [1, 2]),
    ],
)
def test_invalid_rayleigh_parameters(delays, powers):
    with pytest.raises(ValueError):
        rayleigh_channel(delays, powers, 42)


def test_frequency_response_refuses_truncation():
    with pytest.raises(ValueError):
        frequency_response([1, 0, 1], 2)
