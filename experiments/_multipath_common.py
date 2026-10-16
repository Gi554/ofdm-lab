"""Configuration du canal fixe et d'une réalisation Rayleigh documentée."""

import json
from pathlib import Path

import numpy as np

from ofdm_lab.channels import impulse_response, rayleigh_channel

ROOT = Path(__file__).resolve().parents[1]


def load_channels():
    params = json.loads((ROOT / "configs/multipath.json").read_text(encoding="utf-8"))
    fixed = impulse_response([complex(*value) for value in params["fixed_taps"]])
    if params["fixed_normalize_energy"]:
        fixed = fixed / np.linalg.norm(fixed)
    fading = rayleigh_channel(
        params["rayleigh_delays"], params["rayleigh_powers"], params["seed"] + 1
    )
    return params, fixed, fading
