"""Transformées vérifiées par définition DFT, conservation d'énergie et tons connus."""

import numpy as np
import pytest

from ofdm_lab.transforms import fft, ifft, subcarrier_frequencies


@pytest.mark.parametrize("shape", [(8,), (7,), (3, 64), (2, 3, 15)])
def test_inverse_and_parseval(shape):
    rng = np.random.default_rng(42)
    x = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    np.testing.assert_allclose(fft(ifft(x)), x, atol=2e-14)
    np.testing.assert_allclose(ifft(fft(x)), x, atol=2e-14)
    np.testing.assert_allclose(
        np.sum(abs(x) ** 2, axis=-1), np.sum(abs(fft(x)) ** 2, axis=-1), rtol=1e-13
    )
    assert fft(x).shape == shape


def test_matches_explicit_dft_and_signed_tones():
    size = 8
    n = np.arange(size)
    matrix = np.exp(-2j * np.pi * n[:, None] * n[None, :] / size) / np.sqrt(size)
    x = np.arange(size) + 1j * np.arange(size)[::-1]
    np.testing.assert_allclose(fft(x), matrix @ x, atol=3e-14)
    np.testing.assert_allclose(matrix @ matrix.conj().T, np.eye(size), atol=2e-14)
    for tone in [1, -2]:
        spectrum = fft(np.exp(2j * np.pi * tone * n / size) / np.sqrt(size))
        expected = np.zeros(size, dtype=complex)
        expected[tone % size] = 1
        np.testing.assert_allclose(spectrum, expected, atol=2e-14)


def test_frequency_order_and_units():
    np.testing.assert_allclose(
        subcarrier_frequencies(8, 1000), [0, 1000, 2000, 3000, -4000, -3000, -2000, -1000]
    )
    np.testing.assert_allclose(subcarrier_frequencies(5, 2), [0, 2, 4, -4, -2])


@pytest.mark.parametrize("bad", [[], 1, [[1, np.nan]], [np.inf]])
def test_invalid_transform_input(bad):
    for function in [fft, ifft]:
        with pytest.raises(ValueError):
            function(bad)


@pytest.mark.parametrize("n,spacing", [(0, 1), (True, 1), (8, 0), (8, -1), (8, np.inf), (8, True)])
def test_invalid_frequency_parameters(n, spacing):
    with pytest.raises(ValueError):
        subcarrier_frequencies(n, spacing)
