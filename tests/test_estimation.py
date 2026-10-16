import numpy as np
import pytest

from ofdm_lab.channels import apply_multipath, frequency_response
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import (
    PilotLayout,
    estimate_channel_ls,
    interpolation_matrix,
    pilot_energy_budget,
    receive_pilots,
    transmit_pilots,
)
from ofdm_lab.receiver import receive


@pytest.mark.parametrize("order", [2, 4, 16, 64])
@pytest.mark.parametrize("spacing", [2, 4, 8])
def test_flat_channel_roundtrip_and_pilot_exclusion(order, spacing):
    config = OFDMConfig(order=order)
    layout = PilotLayout(config, spacing)
    bits = np.random.default_rng(1).integers(0, 2, 10 * layout.bits_per_frame)
    tx = transmit_pilots(bits, layout)
    assert np.array_equal(
        tx.grid[:, config.active_indices[layout.pilot_positions]],
        np.broadcast_to(layout.pilot_symbols, (10, layout.pilot_positions.size)),
    )
    received = tx.waveform * (0.4 + 0.7j)
    grid = receive(received, config).grid
    estimated = estimate_channel_ls(grid, layout)
    assert np.allclose(estimated[:, config.active_indices], 0.4 + 0.7j)
    for method in ["zf", "mmse"]:
        decided = receive_pilots(received, layout, channel_response=estimated, equalizer=method)
        assert np.array_equal(decided, bits)
    assert decided.size == bits.size


def test_linear_interpolation_lobes_and_no_guard_estimates():
    layout = PilotLayout(OFDMConfig(), 4)
    positions = np.arange(52)
    h = np.where(positions < 26, 2 + positions * (0.01 + 0.03j), -3 + positions * (0.02 - 0.01j))
    grid = np.zeros((2, 64), complex)
    grid[:, layout.config.active_indices[layout.pilot_positions]] = (
        h[layout.pilot_positions] * layout.pilot_symbols
    )
    estimate = estimate_channel_ls(grid, layout)
    assert np.allclose(estimate[:, layout.config.active_indices], h)
    assert np.all(estimate[:, np.setdiff1d(np.arange(64), layout.config.active_indices)] == 0)
    a = interpolation_matrix(layout)
    assert np.allclose(a.sum(axis=1), 1)
    assert np.all(a >= 0)


def test_multipath_oracle_recovers_and_interpolation_bias_is_explicit():
    config = OFDMConfig(order=16)
    layout = PilotLayout(config, 8)
    bits = np.random.default_rng(14).integers(0, 2, 100 * layout.bits_per_frame)
    tx = transmit_pilots(bits, layout)
    h = np.array([1, 0, 0, 0, 0, 0, -0.9])
    received = apply_multipath(tx.waveform, h)[: tx.waveform.size]
    truth = frequency_response(h, 64)
    assert np.array_equal(
        receive_pilots(received, layout, channel_response=truth, equalizer="zf"), bits
    )
    estimate = estimate_channel_ls(receive(received, config).grid, layout)
    active = config.active_indices
    assert np.allclose(
        estimate[:, active[layout.pilot_positions]], truth[active[layout.pilot_positions]]
    )
    expected = truth[active[layout.pilot_positions]] @ interpolation_matrix(layout).T
    assert np.allclose(estimate[:, active], expected)
    assert (
        np.mean(
            abs(estimate[:, active[layout.data_positions]] - truth[active[layout.data_positions]])
            ** 2
        )
        > 0.01
    )


@pytest.mark.parametrize("cp", [0, 6, 16])
def test_energy_budget_including_deterministic_pilot_cp(cp):
    config = OFDMConfig(cp_length=cp, order=4)
    layout = PilotLayout(config, 4)
    frames = 8000
    bits = np.random.default_rng(4).integers(0, 2, frames * layout.bits_per_frame)
    tx = transmit_pilots(bits, layout)
    total = np.sum(abs(tx.with_cp) ** 2, axis=1)
    budget = pilot_energy_budget(layout, 12, "total")
    assert abs(total.mean() - budget["expected_total_energy"]) < 6 * total.std() / np.sqrt(frames)
    assert budget["noise_variance"] == pytest.approx(budget["eb_total_per_data_bit"] / 10**1.2)
    assert pilot_energy_budget(layout, 12, "data")["noise_variance"] == pytest.approx(
        1 / (2 * 10**1.2)
    )
    assert budget["payload_rate_bps"] < config.bits_per_ofdm_symbol * config.sample_rate_hz / (
        64 + cp
    )


def test_estimation_noise_variance_against_analytic_covariance():
    layout = PilotLayout(OFDMConfig(), 4)
    rng = np.random.default_rng(10)
    trials = 5000
    grid = np.zeros((trials, 64), complex)
    grid[:, layout.config.active_indices[layout.pilot_positions]] = layout.pilot_symbols
    noise = (rng.normal(size=grid.shape) + 1j * rng.normal(size=grid.shape)) * np.sqrt(0.02 / 2)
    estimate = estimate_channel_ls(grid + noise, layout)[
        :, layout.config.active_indices[layout.data_positions]
    ]
    a = interpolation_matrix(layout)[layout.data_positions]
    cov = a @ a.T
    expected = 0.02 * np.trace(cov) / a.shape[0]
    variance = 0.02**2 * np.sum(cov**2) / a.shape[0] ** 2
    measured = np.mean(abs(estimate - 1) ** 2)
    assert abs(measured - expected) < 6 * np.sqrt(variance / trials)


@pytest.mark.parametrize("spacing", [0, -1, 1, True, 2.5])
def test_invalid_layout(spacing):
    with pytest.raises(ValueError):
        PilotLayout(OFDMConfig(), spacing)


def test_invalid_payload_grid_and_energy():
    layout = PilotLayout(OFDMConfig())
    for bits in [[], [0], np.ones(layout.bits_per_frame + 1)]:
        with pytest.raises(ValueError):
            transmit_pilots(bits, layout)
    for grid in [[], np.ones(64), np.ones((2, 63)), np.full((2, 64), np.nan)]:
        with pytest.raises(ValueError):
            estimate_channel_ls(grid, layout)
    for db, reference in [(np.nan, "total"), (1, "bad"), (1e6, "total")]:
        with pytest.raises(ValueError):
            pilot_energy_budget(layout, db, reference)
