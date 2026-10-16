"""Égalisation de la chaîne physique complète, CP suffisant et H connu."""

import numpy as np
import pytest

from ofdm_lab import generate_bits
from ofdm_lab.channels import apply_multipath, frequency_response
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.noise import add_awgn
from ofdm_lab.receiver import receive
from ofdm_lab.transmitter import transmit


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("method", ["zf", "mmse"])
def test_known_channel_ideal_equalization(order, method):
    config = OFDMConfig(order=order, cp_length=4)
    bits = generate_bits(100 * config.bits_per_ofdm_symbol, 42)
    tx = transmit(bits, config)
    h = np.array([0.8 + 0.2j, 0, 0, 0, 0.3j])
    stream = apply_multipath(tx.waveform, h)[: tx.waveform.size]
    rx = receive(stream, config, channel_response=frequency_response(h, 64), equalizer=method)
    np.testing.assert_array_equal(rx.bits, bits)
    np.testing.assert_allclose(
        rx.equalized_symbols, tx.grid[:, config.active_indices].ravel(), atol=3e-14
    )


def test_paired_gain_aware_mmse_matches_zf_decisions():
    config = OFDMConfig(order=16)
    tx = transmit(generate_bits(200 * config.bits_per_ofdm_symbol, 43), config)
    h = np.array([1, 0, 0, 0, -0.9])
    H = frequency_response(h, 64)
    stream = add_awgn(apply_multipath(tx.waveform, h)[: tx.waveform.size], 0.2, 44)
    zf = receive(stream, config, channel_response=H, equalizer="zf", noise_variance=0.2)
    mmse = receive(stream, config, channel_response=H, equalizer="mmse", noise_variance=0.2)
    np.testing.assert_array_equal(zf.bits, mmse.bits)
    truth = tx.grid[:, config.active_indices].ravel()
    assert np.mean(abs(mmse.equalized_symbols - truth) ** 2) < np.mean(
        abs(zf.equalized_symbols - truth) ** 2
    )


def test_receiver_rejects_missing_or_malformed_channel():
    config = OFDMConfig()
    tx = transmit(generate_bits(config.bits_per_ofdm_symbol, 42), config)
    with pytest.raises(ValueError):
        receive(tx.waveform, config, equalizer="zf")
    with pytest.raises(ValueError):
        receive(tx.waveform, config, equalizer="zf", channel_response=[1, 2])
    with pytest.raises(ValueError):
        receive(tx.waveform, config, decision_mode="invalid")
