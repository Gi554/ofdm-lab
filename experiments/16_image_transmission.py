"""Transport d'une image locale RGB8, CRC, effacements et rendu diagnostique."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _multipath_common import ROOT, load_channels

from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.estimation import PilotLayout
from ofdm_lab.image_simulation import simulate_image
from ofdm_lab.image_transport import load_image, save_image


def fixture(path, width, height):
    """Mire RGB numérique déterministe, créée par le projet, sans image externe."""
    y, x = np.indices((height, width))
    rgb = np.stack(
        [
            255 * x // max(1, width - 1),
            255 * y // max(1, height - 1),
            np.where(((x // 6 + y // 4) % 2) == 0, 220, 35),
        ],
        axis=-1,
    ).astype(np.uint8)
    rgb[height // 3 : 2 * height // 3, width // 3 : 2 * width // 3] = [240, 200, 30]
    save_image(path, rgb)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image", type=Path, help="PNG local ; défaut : mire fournie par le laboratoire"
    )
    options = parser.parse_args()
    params = json.loads((ROOT / "configs/image.json").read_text(encoding="utf-8"))
    for folder in ["images", "figures", "datasets", "reports"]:
        (ROOT / "results" / folder).mkdir(parents=True, exist_ok=True)
    (ROOT / "assets").mkdir(exist_ok=True)
    if options.image is None:
        path = ROOT / params["image"]
        fixture(path, params["width"], params["height"])
    else:
        path = options.image
    original = load_image(path)
    save_image(ROOT / "results/images/16_original.png", original)
    _, deep, _ = load_channels()
    mild = np.array([complex(*value) for value in params["mild_taps"]])
    if params["mild_normalize_energy"]:
        mild = mild / np.linalg.norm(mild)
    channels = [("awgn", np.array([1.0])), ("mild", mild), ("deep", deep)]
    cases = list(itertools.product(channels, params["orders"], params["ebn0_db"]))
    seeds = np.random.SeedSequence(params["seed"]).generate_state(len(cases))
    rows, ideals, visuals = [], [], []
    chosen = {
        ("awgn", 16, 18, "perfect"),
        ("awgn", 16, 12, "perfect"),
        ("mild", 16, 18, "pilot"),
        ("deep", 16, 18, "perfect"),
    }
    for ((name, taps), order, db), seed in zip(cases, seeds, strict=True):
        config = OFDMConfig(params["n_fft"], params["n_active"], params["cp_length"], order)
        layout = PilotLayout(config, params["pilot_spacing"])
        for method in ["none", "perfect", "pilot"]:
            trial = simulate_image(
                original,
                layout,
                taps,
                db,
                int(seed),
                estimation=method,
                chunk_bytes=params["chunk_bytes"],
            )
            rows.append(dict(channel=name, **trial.metrics))
            if (name, order, db, method) in chosen:
                visuals.append((name, db, method, trial))
                for view in ["diagnostic", "accepted"]:
                    image = getattr(trial.reception, view)
                    output = ROOT / f"results/images/16_{name}_M{order}_{db}dB_{method}_{view}.png"
                    if image is None:
                        output.unlink(missing_ok=True)
                    else:
                        save_image(output, image)
    for (name, taps), order in itertools.product(channels, [2, 4, 16, 64]):
        layout = PilotLayout(OFDMConfig(order=order), params["pilot_spacing"])
        trial = simulate_image(
            original, layout, taps, None, params["seed"], chunk_bytes=params["chunk_bytes"]
        )
        ideals.append(dict(channel=name, **trial.metrics))
    frame = pd.DataFrame(rows)
    exported = frame.copy()
    exported["channel_taps"] = exported.channel_taps.map(json.dumps)
    exported.to_csv(ROOT / "results/datasets/image_transmission.csv", index=False)
    summary = dict(
        seed=params["seed"],
        image_source_name=path.name,
        image_rgb_sha256=hashlib.sha256(original.tobytes()).hexdigest(),
        image_shape=list(original.shape),
        n_channel_bursts=len(cases),
        n_measurements=len(rows),
        scheduled_payload_bits=int(frame[frame.estimation == "perfect"].payload_n_bits.sum()),
        transport_bit_decisions_all_modes=int(frame.transport_n_bits.sum()),
        all_noiseless_reconstructions_passed=all(
            r["transport_bit_errors"] == 0
            and r["accepted_byte_errors"] == 0
            and r["erased_bytes"] == 0
            for r in ideals
        ),
        all_accepted_bytes_match_original=all(
            r["accepted_corrupt_bytes"] in (None, 0) for r in rows
        ),
        noiseless_cases=ideals,
        numpy_version=np.__version__,
    )
    (ROOT / "results/reports/image_transmission.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    axes = axes.ravel()
    axes[0].imshow(original)
    axes[0].set_title("Original RGB8 — mire locale")
    for pair, (name, db, method, trial) in enumerate(visuals):
        for j, view in enumerate(["diagnostic", "accepted"]):
            ax = axes[1 + pair * 2 + j]
            image = getattr(trial.reception, view)
            m = trial.metrics
            if image is None:
                ax.text(
                    0.5,
                    0.5,
                    "Aucun en-tête fiable\nImage non reconstructible",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            else:
                ax.imshow(image)
            title = f"{name}, 16-QAM, {db} dB, {method} — {view}"
            ax.set_title(title, fontsize=9)
            ax.set_xlabel(
                f"BER pixels={m['payload_ber']:.4g} ; "
                f"octets radio erronés={m['raw_payload_byte_errors']}\n"
                f"CRC valides={m['valid_packets']}/{m['transmitted_packets']} ; "
                f"octets effacés={m['erased_bytes']}",
                fontsize=8,
            )
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(
        "OFDM RGB brut : vue diagnostique / blocs acceptés CRC ; magenta = effacement\n"
        "Eb/N0 nominal transport total ; pas de FEC, retransmission ou image oracle à la réception",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(ROOT / "results/figures/16_image_transmission.png", dpi=160)
    plt.close(fig)
    print(json.dumps({k: v for k, v in summary.items() if k != "noiseless_cases"}, indent=2))
    print(
        frame[(frame.order == 16) & (frame.estimation == "perfect")][
            [
                "channel",
                "ebn0_db",
                "payload_bit_errors",
                "payload_ber",
                "raw_payload_byte_errors",
                "valid_packets",
                "invalid_header_packets",
                "corrupt_payload_packets",
                "erased_bytes",
                "reconstructed",
            ]
        ].to_string(index=False)
    )
    if not all(
        [
            summary["all_noiseless_reconstructions_passed"],
            summary["all_accepted_bytes_match_original"],
        ]
    ):
        raise RuntimeError("Validation du transport image échouée ; investiguer.")


if __name__ == "__main__":
    run()
