"""Validation des conventions d'énergie et des statistiques AWGN."""

import numpy as np
import pytest

from ofdm_lab.noise import add_awgn, db_to_linear, ebn0_to_esn0_db, esn0_to_snr_db, noise_variance


def test_known_energy_conversions():
    np.testing.assert_allclose(db_to_linear(10), 10)
    np.testing.assert_allclose(db_to_linear(-10), 0.1)
    np.testing.assert_allclose(ebn0_to_esn0_db(0, 2), 10 * np.log10(2))
    np.testing.assert_allclose(esn0_to_snr_db(10 * np.log10(8), 8), 0, atol=1e-14)
    np.testing.assert_allclose(noise_variance(0, 1), 1)
    np.testing.assert_allclose(noise_variance(10, 4), 0.025)
    np.testing.assert_allclose(noise_variance(10, 4, 2), 0.05)


def test_circular_white_gaussian_noise_statistics():
    size, variance = 400000, 0.4
    noise = add_awgn(np.zeros(size), variance, seed=20261016)
    # Tolérances de six erreurs-types, sous l'hypothèse gaussienne indépendante.
    np.testing.assert_allclose(
        np.mean(abs(noise) ** 2), variance, atol=6 * variance / np.sqrt(size), rtol=0
    )
    for axis in [noise.real, noise.imag]:
        assert abs(axis.mean()) < 6 * np.sqrt(variance / (2 * size))
        assert abs(axis.var() - variance / 2) < 6 * (variance / 2) * np.sqrt(2 / size)
    assert abs(np.mean(noise.real * noise.imag)) < 6 * variance / (2 * np.sqrt(size))
    assert abs(np.mean(noise**2)) < 6 * variance * np.sqrt(2 / size)
    assert abs(np.mean(noise[1:] * noise[:-1].conj())) < 6 * variance / np.sqrt(size)


def test_awgn_reproducible_nonmutating_and_zero_variance():
    signal = np.array([1 + 1j, -1 + 2j])
    original = signal.copy()
    a = add_awgn(signal, 0.2, 42)
    np.testing.assert_array_equal(a, add_awgn(signal, 0.2, 42))
    assert not np.array_equal(a, add_awgn(signal, 0.2, 43))
    np.testing.assert_array_equal(signal, original)
    zero = add_awgn(signal, 0, 42)
    np.testing.assert_array_equal(zero, signal)
    assert not np.shares_memory(zero, signal)
    assert add_awgn([], 0.2, 42).shape == (0,)
    assert add_awgn([1, 2], 0, 42).dtype == np.complex128


def test_noise_is_independent_of_signal_amplitude():
    np.testing.assert_allclose(
        add_awgn(np.ones(100), 0.5, 4) - 1, add_awgn(np.full(100, 10), 0.5, 4) - 10, atol=1e-14
    )


@pytest.mark.parametrize("bad", [True, "1", np.nan, np.inf, -np.inf, 1j, [1]])
def test_invalid_scalar_parameters(bad):
    for function in [
        db_to_linear,
        lambda x: ebn0_to_esn0_db(x, 2),
        lambda x: esn0_to_snr_db(x, 2),
        lambda x: noise_variance(x, 2),
        lambda x: add_awgn([1], x),
        lambda x: noise_variance(0, 2, x),
    ]:
        with pytest.raises(ValueError):
            function(bad)


@pytest.mark.parametrize("bad", [True, 0, -1, 2.0, "2"])
def test_invalid_counts(bad):
    for function in [
        lambda x: ebn0_to_esn0_db(0, x),
        lambda x: esn0_to_snr_db(0, x),
        lambda x: noise_variance(0, x),
    ]:
        with pytest.raises(ValueError):
            function(bad)


@pytest.mark.parametrize("signal", [[[1]], [np.nan], [np.inf]])
def test_invalid_signal(signal):
    with pytest.raises(ValueError):
        add_awgn(signal, 1)


def test_invalid_energy_variance_and_numerical_range():
    for energy in [0, -1]:
        with pytest.raises(ValueError):
            noise_variance(0, 2, energy)
    with pytest.raises(ValueError):
        add_awgn([1], -1)
    for db in [-10000, 10000]:
        with pytest.raises(ValueError):
            db_to_linear(db)
