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


def plot_error_curves(measurements, theoretical_curves, metric: str, path: Path):
    """Taux mesurés avec IC ; zéro erreur représenté par une borne supérieure."""
    fig, ax = plt.subplots(figsize=(10, 6))
    confidence = measurements["confidence"].unique()
    confidence_label = f"{100 * confidence[0]:g} %" if len(confidence) == 1 else "par point"
    for index, (name, group) in enumerate(measurements.groupby("modulation", sort=False)):
        color = f"C{index % 10}"
        curve = theoretical_curves[theoretical_curves["modulation"] == name]
        ax.semilogy(
            curve["ebn0_db"],
            curve[metric + "_theory_exact"],
            color=color,
            label=f"{name} — théorie exacte",
        )
        positive = group[group[metric] > 0]
        ax.errorbar(
            positive["ebn0_db"],
            positive[metric],
            yerr=[
                positive[metric] - positive[metric + "_ci_lower"],
                positive[metric + "_ci_upper"] - positive[metric],
            ],
            fmt="o",
            color=color,
            capsize=3,
            label=f"{name} — simulé, IC {confidence_label}",
        )
        zero = group[group[metric] == 0]
        ax.scatter(zero["ebn0_db"], zero[metric + "_ci_upper"], marker="v", color=color, s=50)
    ax.scatter([], [], marker="v", color="gray", label="0 erreur : borne supérieure IC")
    positive_values = measurements.loc[measurements[metric] > 0, metric]
    zero_upper = measurements.loc[measurements[metric] == 0, metric + "_ci_upper"]
    minimum = (
        min(
            positive_values.min() if len(positive_values) else 1e-3,
            zero_upper.min() if len(zero_upper) else 1e-3,
        )
        / 3
    )
    ax.set(
        xlabel="Eb/N0 (dB)",
        ylabel=f"{metric.upper()} (sans unité)",
        title=f"{metric.upper()} sur AWGN — effectifs fixes, phase connue",
        ylim=(minimum, 1),
    )
    ax.grid(which="both", alpha=0.3)
    ax.legend(fontsize=8, ncol=2)
    ax.text(
        0,
        -0.19,
        "IC BER : bornes simultanées par position binaire ; IC SER : Clopper–Pearson."
        if metric == "ber"
        else "Triangles : borne supérieure après zéro erreur, jamais une probabilité nulle.",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_qam_approximation(curves, path: Path):
    """Écart de l'approximation à la référence exacte ; calcul théorique, sans mesure."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for name in ["16-QAM", "64-QAM"]:
        group = curves[(curves["modulation"] == name) & (curves["ber_theory_exact"] > 0)]
        relative = 100 * (group["ber_qam_approx"] / group["ber_theory_exact"] - 1)
        ax.plot(group["ebn0_db"], relative, label=name)
    ax.set(
        xlabel="Eb/N0 (dB)",
        ylabel="Écart relatif de l'approximation (%)",
        title="QAM — calcul théorique : plus proches voisins contre BER exact",
    )
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_transform_experiment(waveform, spectrum, gram, sample_rate_hz: float, path: Path):
    """Signaux et matrice de Gram effectivement calculés, avec unités physiques choisies."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    n = np.arange(waveform.size)
    axes[0].plot(n / sample_rate_hz * 1e6, waveform.real, label="I")
    axes[0].plot(n / sample_rate_hz * 1e6, waveform.imag, label="Q")
    axes[0].set(xlabel="Temps (µs)", ylabel="Amplitude normalisée", title="IFFT : signal temporel")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[1].stem(
        np.fft.fftshift(np.fft.fftfreq(len(spectrum), d=1 / sample_rate_hz)) / 1e3,
        np.fft.fftshift(abs(spectrum)),
        label="|X[k]|",
    )
    axes[1].set(
        xlabel="Fréquence (kHz)", ylabel="Amplitude normalisée", title="Alphabet fréquentiel"
    )
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    handle = axes[2].imshow(abs(gram), origin="lower", vmin=0, vmax=1)
    axes[2].set(
        xlabel="Indice de sous-porteuse",
        ylabel="Indice de sous-porteuse",
        title="Orthogonalité : |BᴴB|",
    )
    fig.colorbar(handle, ax=axes[2], label="Produit scalaire (sans unité)")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_ofdm_transmission(tx, config, path: Path):
    """Grille, deux symboles avec zones CP et DSP de Welch, sans prétention RF."""
    from scipy.signal import welch

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    width = config.n_fft + config.cp_length
    shown = tx.waveform[: 2 * width]
    t = np.arange(shown.size) / config.sample_rate_hz * 1e6
    axes[0].plot(t, shown.real, label="I")
    axes[0].plot(t, shown.imag, label="Q")
    for start in range(0, len(shown), width):
        if config.cp_length:
            axes[0].axvspan(
                start / config.sample_rate_hz * 1e6,
                (start + config.cp_length) / config.sample_rate_hz * 1e6,
                alpha=0.15,
                color="gray",
                label="CP" if start == 0 else None,
            )
    axes[0].set(
        xlabel="Temps (µs)", ylabel="Amplitude normalisée", title="Signal sérialisé avec CP"
    )
    axes[0].legend(fontsize=8)
    f = np.fft.fftshift(np.fft.fftfreq(config.n_fft, d=1 / config.sample_rate_hz)) / 1e3
    axes[1].stem(f, np.fft.fftshift(abs(tx.grid[0])), label="Premier symbole")
    axes[1].set(
        xlabel="Fréquence (kHz)", ylabel="Amplitude normalisée", title="Allocation native recentrée"
    )
    axes[1].legend(fontsize=8)
    freq, psd = welch(
        tx.waveform,
        fs=config.sample_rate_hz,
        nperseg=min(512, len(tx.waveform)),
        return_onesided=False,
        detrend=False,
    )
    axes[2].plot(
        np.fft.fftshift(freq) / 1e3,
        10 * np.log10(np.maximum(np.fft.fftshift(psd), 1e-30)),
        label="Welch",
    )
    axes[2].set(
        xlabel="Fréquence (kHz)", ylabel="DSP (dB, amplitude²/Hz)", title="DSP discrète estimée"
    )
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_ofdm_ber(frame, path: Path):
    """Comparer les références énergétiques ; triangles = borne haute après zéro erreur."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, order in zip(axes.ravel(), [2, 4, 16, 64], strict=True):
        subset = frame[frame.order == order]
        for (cp, ref), group in subset.groupby(["cp_length", "energy_reference"]):
            label = f"CP={cp}, Eb {ref}"
            (line,) = ax.semilogy(group.ebn0_db, group.ber_theory_exact, label=label + " théorique")
            good = group[group.ber > 0]
            zero = group[group.ber == 0]
            ax.errorbar(
                good.ebn0_db,
                good.ber,
                yerr=[good.ber - good.ber_ci_lower, good.ber_ci_upper - good.ber],
                fmt="o",
                color=line.get_color(),
                capsize=2,
            )
            ax.scatter(zero.ebn0_db, zero.ber_ci_upper, marker="v", color=line.get_color())
        ax.set(
            xlabel="Eb/N0 déclaré (dB)",
            ylabel="BER (sans unité)",
            title={2: "BPSK", 4: "QPSK", 16: "16-QAM", 64: "64-QAM"}[order],
            ylim=(1e-6, 1),
        )
        ax.grid(which="both", alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("OFDM/AWGN : points mesurés et IC 95 % ; triangles = bornes après zéro erreur")
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
