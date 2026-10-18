import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from ofdm_lab.comparison import simulate_comparison
from ofdm_lab.laboratory import (
    LabSettings,
    channel_taps,
    csv_bytes,
    json_bytes,
    png_bytes,
    run_image_lab,
    run_lab,
    run_sweep,
    uploaded_image,
)


def test_lab_trace_matches_existing_engine_and_export_snapshot():
    settings = LabSettings(frames=16)
    result = run_lab(settings)
    assert result["rows"] == simulate_comparison(
        settings.layout(), channel_taps(settings), 12, 16, settings.seed
    )
    assert result["settings"] == asdict(settings)
    assert result["selected"]["method"] == "perfect_zf"
    assert len(result["trace"]["waveform"]) <= 8192
    assert np.isfinite(result["trace"]["psd"]).all()
    assert np.all(np.diff(result["trace"]["frequencies"]) > 0)
    exported = json.loads(json_bytes(result["settings"], result["rows"]))
    assert exported["settings"]["seed"] == settings.seed
    assert "errors_by_carrier_bit" in csv_bytes(result["rows"]).decode("utf-8-sig")


def test_sweep_fixed_channel_and_actual_noise_seeds():
    settings = LabSettings(
        frames=16, channel="Rayleigh statique", equalizer="mmse", estimation="pilot"
    )
    result = run_sweep(settings, [18, 6])
    assert len(result["rows"]) == 10
    assert {r["ebn0_db"] for r in result["rows"]} == {6, 18}
    assert result["rows"][0]["channel_taps"] == result["rows"][-1]["channel_taps"]
    assert result["rows"][0]["seed"] != result["rows"][-1]["seed"]
    assert settings.method == "pilot_mmse"
    assert replace(settings, equalizer="none").method == "none"


@pytest.mark.parametrize("levels", [[], [6, 6], list(range(8)), [31], [float("nan")]])
def test_invalid_sweep(levels):
    with pytest.raises(ValueError):
        run_sweep(LabSettings(), levels)


def test_uploaded_png_roundtrip_and_complete_image_pipeline():
    pixels = np.arange(8 * 8 * 3, dtype=np.uint8).reshape(8, 8, 3)
    data = png_bytes(pixels)
    assert np.array_equal(uploaded_image(data), pixels)
    with pytest.raises(ValueError):
        uploaded_image(b"bad")
    with pytest.raises(ValueError):
        uploaded_image(png_bytes(np.zeros((129, 2, 3), dtype=np.uint8)))
    result = run_image_lab(LabSettings(frames=16, channel="AWGN", ebn0_db=30), pixels)
    assert result["trial"].reception.image_crc_valid is True
    assert np.array_equal(result["trial"].reception.accepted, pixels)


@pytest.mark.parametrize(
    "changes",
    [
        dict(n_fft=8),
        dict(n_active=7),
        dict(frames=1000),
        dict(ebn0_db=-1),
        dict(seed=-1),
        dict(channel="bad"),
    ],
)
def test_invalid_interactive_settings(changes):
    with pytest.raises(ValueError):
        LabSettings(**changes)
