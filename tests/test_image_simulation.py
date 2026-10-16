import numpy as np
import pytest

from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout
from ofdm_lab.image_simulation import simulate_image


def sample():
    return np.arange(5 * 7 * 3, dtype=np.uint8).reshape(5, 7, 3)


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("equalizer", ["zf", "mmse"])
def test_ideal_image_transport_exact(order, equalizer):
    trial = simulate_image(
        sample(),
        PilotLayout(OFDMConfig(order=order)),
        [1, 0, 0.3j],
        None,
        42,
        equalizer=equalizer,
        chunk_bytes=24,
    )
    assert np.array_equal(trial.reception.accepted, sample())
    for key in [
        "payload_bit_errors",
        "transport_bit_errors",
        "raw_payload_byte_errors",
        "erased_bytes",
        "accepted_byte_errors",
        "accepted_corrupt_bytes",
        "ofdm_padding_bit_errors",
    ]:
        assert trial.metrics[key] == 0
    assert trial.metrics["valid_packets"] == 5
    assert trial.metrics["payload_n_bits"] == 840


def test_flat_pilot_image_noiseless_and_noise_reproduces():
    layout = PilotLayout(OFDMConfig(order=16))
    trial = simulate_image(sample(), layout, [0.5 + 0.4j], None, 8, estimation="pilot")
    assert np.array_equal(trial.reception.accepted, sample())
    a = simulate_image(sample(), layout, [1], 0, 7)
    b = simulate_image(sample(), layout, [1], 0, 7)
    assert a.metrics == b.metrics
    assert a.metrics["payload_bit_errors"] > 0
    assert (
        a.metrics["header_bit_errors"]
        + a.metrics["packet_padding_bit_errors"]
        + a.metrics["payload_bit_errors"]
        == a.metrics["transport_bit_errors"]
    )
    assert a.metrics["accepted_corrupt_bytes"] in (None, 0)


@pytest.mark.parametrize("estimation,equalizer", [("bad", "zf"), ("perfect", "bad")])
def test_invalid_methods(estimation, equalizer):
    with pytest.raises(ValueError):
        simulate_image(
            sample(),
            PilotLayout(OFDMConfig()),
            [1],
            12,
            1,
            estimation=estimation,
            equalizer=equalizer,
        )
