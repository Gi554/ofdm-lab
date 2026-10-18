"""Services du laboratoire interactif ; orchestration, limites et exports en mémoire."""

import json
import struct
from dataclasses import asdict, dataclass
from io import BytesIO

import matplotlib.image as mpimg
import numpy as np
import pandas as pd
from scipy.signal import welch

from .channels import rayleigh_channel
from .comparison import simulate_comparison
from .configuration import OFDMConfig
from .estimation import PilotLayout
from .image_simulation import simulate_image
from .image_transport import encode_image, load_image
from .noise import _positive_integer

CHANNELS = ["AWGN", "Multitrajet modéré", "Multitrajet à creux", "Rayleigh statique"]
METHODS = {
    "none": "Sans correction",
    "perfect_zf": "Canal connu · ZF",
    "perfect_mmse": "Canal connu · MMSE",
    "pilot_zf": "Pilotes LS · ZF",
    "pilot_mmse": "Pilotes LS · MMSE",
}


@dataclass(frozen=True)
class LabSettings:
    n_fft: int = 64
    n_active: int = 52
    cp_length: int = 16
    order: int = 16
    ebn0_db: float = 12.0
    frames: int = 128
    seed: int = 20261018
    pilot_spacing: int = 4
    channel: str = "Multitrajet modéré"
    estimation: str = "perfect"
    equalizer: str = "zf"

    def __post_init__(self):
        if self.n_fft not in (32, 64, 128, 256):
            raise ValueError("Choisir une FFT de 32, 64, 128 ou 256 points.")
        if not 8 <= self.n_active <= self.n_fft - 2:
            raise ValueError("Il faut au moins 8 porteuses actives, sans DC ni Nyquist.")
        if not 1 <= _positive_integer(self.frames, "Les trames") <= 512:
            raise ValueError("Le calcul interactif est limité à 512 trames.")
        if (
            not isinstance(self.seed, int)
            or isinstance(self.seed, bool)
            or not 0 <= self.seed < 2**32
        ):
            raise ValueError("La graine doit être un entier entre 0 et 2³²−1.")
        if not np.isfinite(self.ebn0_db) or not 0 <= self.ebn0_db <= 30:
            raise ValueError("Eb/N0 doit être entre 0 et 30 dB.")
        if (
            self.channel not in CHANNELS
            or self.estimation not in ("none", "perfect", "pilot")
            or self.equalizer not in ("none", "zf", "mmse")
        ):
            raise ValueError("Canal, estimation ou égaliseur inconnu.")
        self.layout()

    def layout(self):
        return PilotLayout(
            OFDMConfig(self.n_fft, self.n_active, self.cp_length, self.order, 960000 / self.n_fft),
            self.pilot_spacing,
        )

    @property
    def method(self):
        return (
            "none"
            if self.equalizer == "none" or self.estimation == "none"
            else f"{self.estimation}_{self.equalizer}"
        )


def channel_taps(settings):
    if settings.channel == "AWGN":
        return np.array([1.0 + 0j])
    if settings.channel == "Rayleigh statique":
        return rayleigh_channel([0, 2, 6], [0.6, 0.3, 0.1], settings.seed + 1)
    taps = np.array(
        [1, 0.25j, 0, -0.15]
        if settings.channel == "Multitrajet modéré"
        else [1, 0, 0, 0, 0, 0, -0.95],
        dtype=complex,
    )
    return taps / np.linalg.norm(taps)


def run_lab(settings):
    rows, trace = simulate_comparison(
        settings.layout(),
        channel_taps(settings),
        settings.ebn0_db,
        settings.frames,
        settings.seed,
        return_trace=True,
    )
    frequencies, power = welch(
        trace["waveform"],
        fs=960000,
        nperseg=min(256, trace["waveform"].size),
        return_onesided=False,
        scaling="density",
    )
    trace["frequencies"] = np.fft.fftshift(frequencies)
    trace["psd"] = np.fft.fftshift(power)
    return dict(
        settings=asdict(settings),
        rows=rows,
        trace=trace,
        selected=next(r for r in rows if r["method"] == settings.method),
    )


def run_sweep(settings, levels):
    points = [float(x) for x in levels]
    if (
        not points
        or len(points) > 7
        or len(set(points)) != len(points)
        or any(not np.isfinite(x) or not 0 <= x <= 30 for x in points)
    ):
        raise ValueError("Sélectionner de 1 à 7 valeurs Eb/N0 distinctes entre 0 et 30 dB.")
    seeds = np.random.SeedSequence(settings.seed).generate_state(len(points))
    taps = channel_taps(settings)
    rows = []
    for db, seed in zip(sorted(points), seeds, strict=True):
        rows.extend(simulate_comparison(settings.layout(), taps, db, settings.frames, int(seed)))
    return dict(settings=asdict(settings), rows=rows, levels=sorted(points))


def csv_bytes(rows):
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        if any(isinstance(x, (list, dict)) for x in frame[column]):
            frame[column] = frame[column].map(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
            )
    return frame.to_csv(index=False).encode("utf-8-sig")


def json_bytes(settings, rows):
    return json.dumps(
        dict(settings=settings, measurements=rows), ensure_ascii=False, indent=2, allow_nan=False
    ).encode("utf-8")


def png_bytes(image):
    output = BytesIO()
    mpimg.imsave(output, image, format="png")
    return output.getvalue()


def uploaded_image(data):
    if len(data) > 2 * 1024 * 1024 or len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Choisir un PNG valide de moins de 2 Mio.")
    width, height = struct.unpack(">II", data[16:24])
    if not width or not height or max(width, height) > 128:
        raise ValueError("L’image interactive doit mesurer au maximum 128×128 pixels.")
    return load_image(data)


def run_image_lab(settings, image):
    layout = settings.layout()
    if len(encode_image(image)) * 8 > 4096 * layout.bits_per_frame:
        raise ValueError(
            (
                "Image trop grande pour ces réglages : réduire ses dimensions ou "
                "augmenter la capacité des trames."
            )
        )
    trial = simulate_image(
        image,
        layout,
        channel_taps(settings),
        settings.ebn0_db,
        settings.seed,
        estimation="none" if settings.method == "none" else settings.estimation,
        equalizer="zf" if settings.equalizer == "none" else settings.equalizer,
    )
    return dict(settings=asdict(settings), original=image.copy(), trial=trial)
