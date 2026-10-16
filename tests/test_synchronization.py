import numpy as np
import pytest

from ofdm_lab.channels import apply_multipath
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.synchronization import apply_frequency_offset, cfo_tone_response, estimate_cfo_cp
from ofdm_lab.transmitter import transmit


@pytest.mark.parametrize("offset", [-0.49, -0.2, 0, 0.15, 0.49, 0.7])
@pytest.mark.parametrize("taps", [[1], [1, 0, 0, 0.4j]])
def test_cp_estimator_exact_and_modulo(offset, taps):
    config = OFDMConfig()
    bits = np.random.default_rng(8).integers(0, 2, 30 * config.bits_per_ofdm_symbol)
    tx = transmit(bits, config)
    samples = apply_multipath(tx.waveform, taps)[: tx.waveform.size]
    shifted = apply_frequency_offset(samples, offset, config.n_fft)
    result = estimate_cfo_cp(shifted, config, channel_memory=len(taps) - 1)
    expected = (offset + 0.5) % 1 - 0.5
    assert result.normalized_offset == pytest.approx(expected, abs=1e-14)
    assert result.coherence == pytest.approx(1, abs=1e-14)
    assert result.n_pairs == 30 * (config.cp_length - len(taps) + 1)


def test_inverse_energy_and_continuous_chunks():
    rng = np.random.default_rng(4)
    x = rng.normal(size=123) + 1j * rng.normal(size=123)
    y = apply_frequency_offset(x, 0.23, 64)
    assert np.allclose(apply_frequency_offset(y, -0.23, 64), x, atol=1e-14)
    assert np.linalg.norm(y) == pytest.approx(np.linalg.norm(x))
    chunks = np.r_[
        apply_frequency_offset(x[:45], 0.23, 64),
        apply_frequency_offset(x[45:], 0.23, 64, start_sample=45),
    ]
    assert np.allclose(chunks, y)


@pytest.mark.parametrize("offset", [0, 0.1, 0.3, 1])
def test_tone_leakage_against_geometric_sum(offset):
    response = cfo_tone_response(offset, 64)
    n = np.arange(64)
    independent = np.array([np.mean(np.exp(2j * np.pi * (offset - k) * n / 64)) for k in range(64)])
    assert np.allclose(response, independent, atol=2e-14)
    assert np.sum(abs(response) ** 2) == pytest.approx(1)
    if offset == 1:
        assert abs(response[1]) == pytest.approx(1)


def test_noise_estimator_improves_with_snr():
    config = OFDMConfig()
    rng = np.random.default_rng(12)
    bits = rng.integers(0, 2, 100 * config.bits_per_ofdm_symbol)
    x = apply_frequency_offset(transmit(bits, config).waveform, 0.2, 64)
    noise = rng.normal(size=x.size) + 1j * rng.normal(size=x.size)
    low = estimate_cfo_cp(x + noise, config).normalized_offset
    high = estimate_cfo_cp(x + 0.01 * noise, config).normalized_offset
    assert abs(high - 0.2) < abs(low - 0.2)
    assert abs(high - 0.2) < 0.001


@pytest.mark.parametrize(
    "signal,offset,size,start",
    [
        ([], 0, 64, 0),
        ([1], np.nan, 64, 0),
        ([1], 0, 0, 0),
        ([[1]], 0, 64, 0),
        ([1], 0, 64, -1),
        ([1], 0, 64, True),
    ],
)
def test_invalid_offset(signal, offset, size, start):
    with pytest.raises(ValueError):
        apply_frequency_offset(signal, offset, size, start_sample=start)


@pytest.mark.parametrize(
    "cp,memory,signal",
    [
        (0, 0, np.ones(64)),
        (3, 3, np.ones(67)),
        (16, 0, np.zeros(80)),
        (16, 0, np.ones(79)),
        (16, 0, np.ones((1, 80))),
    ],
)
def test_invalid_cp(cp, memory, signal):
    with pytest.raises(ValueError):
        estimate_cfo_cp(signal, OFDMConfig(cp_length=cp), channel_memory=memory)


@pytest.mark.parametrize("order", [2, 4, 16, 64])
def test_noiseless_correction_restores_receiver(order):
    from ofdm_lab.receiver import receive

    config = OFDMConfig(order=order)
    bits = np.random.default_rng(18).integers(0, 2, 100 * config.bits_per_ofdm_symbol)
    tx = transmit(bits, config)
    shifted = apply_frequency_offset(tx.waveform, 0.31, 64)
    estimate = estimate_cfo_cp(shifted, config)
    corrected = apply_frequency_offset(shifted, -estimate.normalized_offset, 64)
    assert np.array_equal(receive(corrected, config).bits, bits)


def test_fft_projection_offdiagonal_and_common_phase():
    # Matrice indépendante explicite F D F* ; D conserve l'orthogonalité entre
    # les signaux émis mais leur projection sur la base du récepteur n'est plus diagonale.
    n = 16
    f = np.exp(-2j * np.pi * np.outer(np.arange(n), np.arange(n)) / n) / np.sqrt(n)
    d = np.diag(np.exp(2j * np.pi * 0.2 * np.arange(n) / n))
    matrix = f @ d @ f.conj().T
    response = cfo_tone_response(0.2, n)
    assert np.allclose(matrix[:, 0], response)
    assert np.allclose(matrix.conj().T @ matrix, np.eye(n), atol=1e-14)
    assert np.linalg.norm(matrix - np.diag(np.diag(matrix))) > 0.5
    a = apply_frequency_offset(np.ones(n), 0.2, n, start_sample=32)
    b = apply_frequency_offset(np.ones(n), 0.2, n)
    assert np.allclose(a, b * np.exp(2j * np.pi * 0.2 * 32 / n))
