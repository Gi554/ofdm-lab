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


def plot_constellation_clouds(clouds, ideal, title: str, path: Path):
    """Comparer des nuages reçus sur des axes communs ; points réellement simulés."""
    fig, axes = plt.subplots(1, len(clouds), figsize=(5 * len(clouds), 5), squeeze=False)
    extent = (
        max(1.5, *(float(np.max(np.abs(np.concatenate((y.real, y.imag))))) for _, y in clouds))
        * 1.1
    )
    for ax, (label, received) in zip(axes[0], clouds, strict=True):
        ax.scatter(received.real, received.imag, s=5, alpha=0.2, label="Symboles reçus")
        ax.scatter(ideal.real, ideal.imag, marker="x", c="black", s=50, label="Alphabet idéal")
        ax.set(
            xlabel="I (amplitude normalisée)",
            ylabel="Q (amplitude normalisée)",
            title=label,
            xlim=(-extent, extent),
            ylim=(-extent, extent),
        )
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
