"""Validation des expressions AWGN par références analytiques indépendantes."""

import numpy as np
import pytest
from scipy.special import erfc

from ofdm_lab.theory import ber_awgn, q_function, qam_ber_nearest_neighbor, ser_awgn


def test_q_and_bpsk_qpsk_reference():
    np.testing.assert_allclose(q_function([0, 1, np.inf, -np.inf]), [0.5, 0.158655253931457, 0, 1])
    np.testing.assert_allclose(ber_awgn(0, 2), 0.07864960352514257)
    np.testing.assert_allclose(ber_awgn(0, 4), ber_awgn(0, 2))
    pb = ber_awgn(0, 4)
    np.testing.assert_allclose(ser_awgn(0, 4), 2 * pb - pb * pb)
    np.testing.assert_allclose(ser_awgn(0, 2), pb)


@pytest.mark.parametrize("ebn0", [-8, 0, 6, 12])
def test_exact_16qam_matches_closed_form(ebn0):
    a = np.sqrt(0.8 * 10 ** (ebn0 / 10))

    def q(x):
        return 0.5 * erfc(x / np.sqrt(2))

    closed = 0.75 * q(a) + 0.5 * q(3 * a) - 0.25 * q(5 * a)
    np.testing.assert_allclose(ber_awgn(ebn0, 16), closed, rtol=1e-11, atol=1e-15)


@pytest.mark.parametrize("order", [2, 4, 16, 64])
def test_limits_and_monotonicity(order):
    np.testing.assert_allclose(ber_awgn(-100, order), 0.5, atol=2e-5)
    np.testing.assert_allclose(ser_awgn(-100, order), 1 - 1 / order, atol=2e-5)
    ber = [ber_awgn(db, order) for db in [-4, 0, 4, 8, 12, 16]]
    assert np.all(np.diff(ber) < 0)
    assert 0 <= ber_awgn(30, order) < 1e-8


@pytest.mark.parametrize("order", [16, 64])
def test_qam_approximation_is_labeled_and_asymptotic(order):
    assert ber_awgn(-4, order) > qam_ber_nearest_neighbor(-4, order)
    np.testing.assert_allclose(ber_awgn(16, order), qam_ber_nearest_neighbor(16, order), rtol=1e-8)


@pytest.mark.parametrize("bad", [True, 2.0, "4", 8, 32, 0])
def test_invalid_orders(bad):
    for function in [ber_awgn, ser_awgn, qam_ber_nearest_neighbor]:
        with pytest.raises(ValueError):
            function(0, bad)
