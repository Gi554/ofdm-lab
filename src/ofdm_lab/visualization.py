"""Figures scientifiques ; aucune génération de données dans ce module."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_bits(bits, path: Path):
    """Tracer les 64 premiers bits, avec index sans unité temporelle supposée."""
    fig, ax = plt.subplots(figsize=(9, 3))
    shown = np.asarray(bits)[:64]
    ax.step(np.arange(shown.size), shown, where="mid", label="Bits générés")
    ax.set(
        xlabel="Indice du bit (sans unité)",
        ylabel="Valeur binaire (sans unité)",
        title="Séquence binaire pseudo-aléatoire",
        yticks=[0, 1],
        ylim=(-0.2, 1.2),
    )
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_constellation(symbols, labels, title: str, path: Path):
    """Tracer des points idéaux annotés, axes I/Q normalisés."""
    dense = len(labels) > 16
    fig, ax = plt.subplots(figsize=(9, 9) if dense else (5, 5))
    ax.scatter(symbols.real, symbols.imag, label="Symboles idéaux")
    for z, label in zip(symbols, labels, strict=True):
        ax.annotate(
            label,
            (z.real, z.imag),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8 if dense else 10,
        )
    ax.set(
        xlabel="I (amplitude normalisée)",
        ylabel="Q (amplitude normalisée)",
        title=title,
        xlim=(-1.5, 1.5),
        ylim=(-1.5, 1.5),
    )
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
