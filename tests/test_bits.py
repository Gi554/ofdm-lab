"""Validation de la fonctionnalité scientifique associée."""

import numpy as np
import pytest

from ofdm_lab import generate_bits


def test_generation_reproducible():
    a = generate_bits(10000, 42)
    np.testing.assert_array_equal(a, generate_bits(10000, 42))
    assert a.dtype == np.uint8
    assert a.shape == (10000,)
    assert set(np.unique(a)) == {0, 1}
    assert not np.array_equal(a, generate_bits(10000, 43))


@pytest.mark.parametrize("count", [-1, 1.5, True, "8"])
def test_bad_count(count):
    with pytest.raises(ValueError):
        generate_bits(count)


def test_generator_does_not_modify_global_state():
    np.random.seed(2718)
    expected = np.random.random(5)
    np.random.seed(2718)
    generate_bits(100, 42)
    np.testing.assert_array_equal(np.random.random(5), expected)
