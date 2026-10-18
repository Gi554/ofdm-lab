"""Laboratoire Streamlit : interface des modules scientifiques validés."""

from dataclasses import asdict
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from ofdm_lab.image_transport import load_image
from ofdm_lab.laboratory import (
    CHANNELS,
    METHODS,
    LabSettings,
    csv_bytes,
    json_bytes,
    png_bytes,
    run_image_lab,
    run_lab,
    run_sweep,
    uploaded_image,
)

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="OFDM Lab", page_icon="〰️", layout="wide")
st.markdown(
    """<style>
.block-container {padding-top:4rem;max-width:1500px}
h1,h2,h3 {letter-spacing:-.025em}
[data-testid="stSidebar"] {border-right:1px solid #dde5ec}
[data-testid="stMetric"] {background:white;border:1px solid #dde5ec;border-radius:12px;padding:16px}
.hero {border-bottom:1px solid #d9e2eb;padding:0 0 22px;margin-bottom:24px}
.eyebrow {font-size:12px;font-weight:700;letter-spacing:.18em;color:#087f75}
.hero h1 {font-size:42px;line-height:1.15;margin:9px 0;color:#15263b}
.hero p {color:#53677d;margin:0;max-width:750px}
.pill {display:inline-block;background:#e0f3ee;color:#076b62;padding:5px 11px;border-
  radius:20px;font-size:12px;margin-top:14px}
</style>""",
    unsafe_allow_html=True,
)


def export_rows(result, prefix):
    left, right = st.columns(2)
    left.download_button(
        "Télécharger les données CSV",
        csv_bytes(result["rows"]),
        file_name=prefix + ".csv",
        mime="text/csv",
        key=prefix + "_csv",
    )
    right.download_button(
        "Télécharger les paramètres JSON",
        json_bytes(
            dict(result["settings"], sweep_levels_db=result["levels"])
            if "levels" in result
            else result["settings"],
            result["rows"],
        ),
        file_name=prefix + ".json",
        mime="application/json",
        key=prefix + "_json",
    )


def figure_export(fig, name):
    st.pyplot(fig, width="stretch")
    output = BytesIO()
    fig.savefig(output, format="png", dpi=180, bbox_inches="tight")
    st.download_button(
        "Exporter ce graphique PNG",
        output.getvalue(),
        file_name=name + ".png",
        mime="image/png",
        key=name + "_png",
    )
    plt.close(fig)


def metrics(row):
    columns = st.columns(4)
    columns[0].metric("BER observé", f"{row['ber']:.3g}")
    columns[1].metric("Erreurs binaires", f"{row['bit_errors']:,}")
    columns[2].metric("MSE des symboles", f"{row['symbol_mse']:.4g}")
    columns[3].metric("Débit utile (Mbit/s)", f"{row['payload_rate_bps'] / 1e6:.3f}")
    st.caption(f"Effectif du calcul : {row['n_bits']:,} bits utiles.")
    if row["cp_sufficient"]:
        st.caption(
            (
                f"IC BER conservateur 95 % : [{row['ber_ci_lower']:.3g} ; "
                f"{row['ber_ci_upper']:.3g}] · par porteuse/bit, canal fixé. Zéro erreur "
                f"observée ne signifie pas BER théorique nul."
            )
        )
    else:
        st.warning(
            (
                "CP inférieur à la mémoire du canal : ISI présente. BER et MSE "
                "descriptifs, sans IC binomial ni référence diagonale."
            )
        )


with st.sidebar:
    st.markdown("### 〰️ OFDM LAB")
    page = st.radio("Espace", ["Simulation", "Comparaisons", "Image", "Repères"], key="page")
    st.divider()
    st.caption("CONFIGURATION DE TRANSMISSION")
    order = st.selectbox(
        "Modulation",
        [2, 4, 16, 64],
        index=2,
        format_func=lambda m: {2: "BPSK", 4: "QPSK", 16: "16-QAM", 64: "64-QAM"}[m],
        key="order",
    )
    size = st.selectbox("Taille FFT", [32, 64, 128, 256], index=1, key="n_fft")
    active = st.slider(
        "Porteuses actives", 8, size - 2, size * 13 // 16, step=2, key=f"active_{size}"
    )
    cp = st.slider("Préfixe cyclique (échantillons)", 0, size, min(16, size), key=f"cp_{size}")
    pitch = st.selectbox("Pas maximal entre pilotes", [2, 4, 8], index=1, key="pilot_spacing")
    channel = st.selectbox("Canal", CHANNELS, index=1, key="channel")
    ebn0 = st.slider("Eb total/N0 (dB)", 0, 30, 12, key="ebn0")
    enabled = st.toggle("Égalisation", True, key="enabled")
    estimate = st.selectbox(
        "Connaissance du canal",
        ["Canal connu", "Pilotes LS", "Sans correction"],
        key="estimation",
        disabled=not enabled,
    )
    eq = st.selectbox(
        "Égaliseur",
        ["ZF", "MMSE"],
        key="equalizer",
        disabled=not enabled or estimate == "Sans correction",
    )
    frames = st.slider("Trames pour les essais binaires", 16, 512, 128, step=16, key="frames")
    seed = st.number_input("Graine reproductible", 0, 2**32 - 1, 20261018, step=1, key="seed")
    st.caption("Fs = 960 kHz · Es alphabet = 1 · timing parfait · CFO nul")

try:
    settings = LabSettings(
        n_fft=size,
        n_active=active,
        cp_length=cp,
        order=order,
        ebn0_db=float(ebn0),
        frames=frames,
        seed=seed,
        pilot_spacing=pitch,
        channel=channel,
        estimation={"Canal connu": "perfect", "Pilotes LS": "pilot", "Sans correction": "none"}[
            estimate
        ],
        equalizer=eq.lower() if enabled else "none",
    )
except ValueError as error:
    st.error(str(error))
    st.stop()

headings = {
    "Simulation": (
        "Du signal aux résultats.",
        "Observez une transmission OFDM et reliez les paramètres aux erreurs mesurées.",
    ),
    "Comparaisons": (
        "Mesurez les compromis.",
        "Comparez les méthodes sur les mêmes ressources, puis conservez vos expériences.",
    ),
    "Image": (
        "Des bits aux pixels.",
        "Transmettez une image et distinguez les pixels reçus des blocs acceptés.",
    ),
    "Repères": (
        "Comprendre les mesures.",
        "Hypothèses, conventions et limites du laboratoire scientifique.",
    ),
}
st.markdown(
    (
        f'<div class="hero"><div class="eyebrow">LABORATOIRE DE TRANSMISSIONS '
        f"NUMÉRIQUES</div>"
        f"<h1>{headings[page][0]}</h1>"
        f"<p>{headings[page][1]}</p>"
        '<span class="pill">OFDM · bande de base complexe</span></div>'
    ),
    unsafe_allow_html=True,
)

if page == "Simulation":
    launch = st.button("Lancer la simulation", type="primary", key="run")
    if launch or "result" not in st.session_state:
        try:
            with st.spinner("Transmission, canal et décisions…"):
                st.session_state.result = run_lab(settings)
        except (ValueError, FloatingPointError) as error:
            st.error(f"Calcul impossible : {error}")
            st.stop()
    result = st.session_state.result
    if result["settings"] != asdict(settings):
        st.info(
            (
                "Réglages modifiés : les résultats ci-dessous appartiennent au dernier "
                "calcul. Relancez pour les actualiser."
            )
        )
    snapshot = result["settings"]
    row = result["selected"]
    st.caption(
        (
            f"DERNIER CALCUL · M={snapshot['order']} · N={snapshot['n_fft']} · "
            f"CP={snapshot['cp_length']} · {snapshot['channel']} · "
            f"{METHODS[row['method']]} · Eb/N0={snapshot['ebn0_db']:g} dB"
        )
    )
    metrics(row)
    tabs = st.tabs(["Constellations", "Spectre & canal", "Mesures & exports"])
    with tabs[0]:
        trace = result["trace"]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, label, cloud in [
            (axes[0], "Réception brute", trace["symbols"]["none"]),
            (axes[1], METHODS[row["method"]], trace["symbols"][row["method"]]),
        ]:
            ax.scatter(cloud.real, cloud.imag, s=7, alpha=0.4, color="#087f75", label="Reçus")
            ideal = np.unique(trace["transmitted"])
            ax.scatter(ideal.real, ideal.imag, s=36, marker="+", color="#c05b18", label="Émis")
            ax.set(title=label, xlabel="En phase I", ylabel="Quadrature Q", aspect="equal")
            ax.grid(alpha=0.2)
            ax.legend(fontsize=8)
        fig.tight_layout()
        figure_export(fig, "constellations")
        st.caption(
            (
                "Au plus 2 048 symboles de données affichés. Estimations avant décision ; "
                "MMSE conserve son gain résiduel dans cette vue, compensé lors des "
                "décisions."
            )
        )
    with tabs[1]:
        trace = result["trace"]
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(
            trace["frequencies"] / 1000,
            10 * np.log10(np.maximum(trace["psd"], 1e-30)),
            color="#087f75",
        )
        axes[0].set(
            title="Spectre émis (Welch)",
            xlabel="Fréquence (kHz)",
            ylabel="DSP (dB, unités normalisées/Hz)",
        )
        config = LabSettings(**snapshot).layout().config
        indices = config.active_indices
        freq = np.fft.fftfreq(config.n_fft, d=1 / config.sample_rate_hz)[indices] / 1000
        axes[1].plot(freq, abs(trace["channel"][indices]), label="H réel", color="#15263b")
        axes[1].plot(
            freq,
            abs(trace["estimated_channel"][indices]),
            ".",
            label="H estimé, première trame",
            color="#087f75",
        )
        axes[1].set(
            title="Réponse sur les porteuses actives", xlabel="Fréquence (kHz)", ylabel="Module |H|"
        )
        axes[1].legend(fontsize=8)
        for ax in axes:
            ax.grid(alpha=0.2)
        fig.tight_layout()
        figure_export(fig, "spectre_canal")
        st.caption(
            (
                "DSP estimée sur au plus 8 192 échantillons. Les gardes et DC ne sont pas "
                "estimées par les pilotes. Le canal Rayleigh reste une réalisation "
                "statique conditionnelle."
            )
        )
    with tabs[2]:
        st.dataframe(
            pd.DataFrame(result["rows"])[
                [
                    "method",
                    "bit_errors",
                    "n_bits",
                    "ber",
                    "ber_ci_lower",
                    "ber_ci_upper",
                    "channel_mse_data",
                    "symbol_mse",
                ]
            ],
            hide_index=True,
            width="stretch",
        )
        export_rows(result, "simulation")
        with st.expander("Paramètres enregistrés et bilan énergétique"):
            st.json(
                dict(
                    parameters=snapshot,
                    noise_variance=row["noise_variance"],
                    pilots=row["n_pilots"],
                    data=row["n_data"],
                    overhead_factor=row["overhead_factor"],
                    energy_reference=row["energy_reference"],
                )
            )
    if st.button("Conserver cette expérience", key="save"):
        history = st.session_state.get("history", [])
        history.append(
            dict(
                **snapshot,
                method=row["method"],
                ber=row["ber"],
                bit_errors=row["bit_errors"],
                n_bits=row["n_bits"],
                symbol_mse=row["symbol_mse"],
            )
        )
        st.session_state.history = history[-8:]
        st.success("Expérience ajoutée aux comparaisons de cette session (8 maximum).")

elif page == "Comparaisons":
    st.subheader("Balayage du niveau de bruit")
    levels = st.multiselect(
        "Eb total/N0 à comparer (dB)", list(range(0, 31, 3)), default=[0, 6, 12, 18], key="levels"
    )
    st.caption(
        (
            "Cinq méthodes appariées par point. Canal fixé, graines de bruit/données "
            "dérivées et exportées ; jusqu’à 7 points."
        )
    )
    if st.button("Calculer le balayage", type="primary", key="sweep"):
        try:
            with st.spinner("Calcul des points BER…"):
                st.session_state.sweep_result = run_sweep(settings, levels)
        except (ValueError, FloatingPointError) as error:
            st.error(str(error))
    if "sweep_result" in st.session_state:
        result = st.session_state.sweep_result
        # Préserver les sessions ouvertes avant l'ajout des niveaux dans le snapshot.
        result.setdefault("levels", sorted({r["ebn0_db"] for r in result["rows"]}))
        snapshot = result["settings"]
        st.caption(
            f"BALAYAGE ENREGISTRÉ · M={snapshot['order']} · N={snapshot['n_fft']} · "
            f"CP={snapshot['cp_length']} · {snapshot['channel']} · "
            f"{snapshot['frames']} trames par point"
        )
        if result["settings"] != asdict(settings) or result["levels"] != sorted(levels):
            st.info(
                (
                    "Le balayage affiché conserve les paramètres de son dernier calcul, "
                    "disponibles en JSON."
                )
            )
        frame = pd.DataFrame(result["rows"])
        fig, ax = plt.subplots(figsize=(9, 4))
        for method, group in frame.groupby("method", sort=False):
            good = group.ber_ci_lower.notna()
            ax.plot(group.ebn0_db, group.ber, "o-", label=METHODS[method])
            if good.all():
                ax.fill_between(group.ebn0_db, group.ber_ci_lower, group.ber_ci_upper, alpha=0.07)
        reference = frame[frame.method == "perfect_zf"]
        if reference.ber_theory_conditional.notna().all():
            ax.plot(
                reference.ebn0_db,
                reference.ber_theory_conditional,
                "k:",
                label="Référence conditionnelle, H connu",
            )
        ax.set(
            xlabel="Eb total/N0 (dB)",
            ylabel="BER données",
            title="Points mesurés et IC conservateurs à 95 % par ligne",
        )
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
        fig.tight_layout()
        figure_export(fig, "comparaison_ber")
        if not frame.cp_sufficient.all():
            st.warning(
                "CP insuffisant : points descriptifs, sans IC ni référence théorique diagonale."
            )
        export_rows(result, "balayage")
    st.subheader("Expériences conservées")
    history = st.session_state.get("history", [])
    if history:
        st.dataframe(pd.DataFrame(history), hide_index=True, width="stretch")
        st.download_button(
            "Exporter l’historique CSV",
            csv_bytes(history),
            file_name="experiences.csv",
            mime="text/csv",
        )
        if st.button("Effacer l’historique", key="clear_history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info(
            "Conservez une expérience depuis Simulation pour comparer plusieurs configurations ici."
        )

elif page == "Image":
    st.subheader("Source de pixels")
    upload = st.file_uploader("PNG local, au maximum 128×128 pixels", type=["png"], key="upload")
    try:
        original = (
            uploaded_image(upload.getvalue())
            if upload is not None
            else load_image(ROOT / "assets/test_pattern.png")
        )
    except (ValueError, OSError) as error:
        st.error(f"Image illisible : {error}")
        st.stop()
    st.caption(
        (
            "Mire de démonstration utilisée en l’absence de fichier. Alpha composé "
            "sur blanc. Les fichiers restent en mémoire de cette session et ne sont "
            "pas écrits dans le dépôt."
        )
    )
    if st.button("Transmettre l’image", type="primary", key="image_run"):
        try:
            with st.spinner("Paquétisation, transmission OFDM et contrôle des CRC…"):
                st.session_state.image_result = run_image_lab(settings, original)
        except (ValueError, FloatingPointError) as error:
            st.error(str(error))
    if "image_result" in st.session_state:
        result = st.session_state.image_result
        trial = result["trial"]
        m = trial.metrics
        if result["settings"] != asdict(settings) or not np.array_equal(
            result["original"], original
        ):
            st.info(
                (
                    "L’affichage appartient à la dernière transmission ; relancez pour "
                    "utiliser les nouveaux réglages ou la nouvelle image."
                )
            )
        columns = st.columns(3)
        columns[0].image(result["original"], caption="Original du dernier calcul", width="stretch")
        for column, view, title in [
            (columns[1], "diagnostic", "Pixels diagnostiques"),
            (columns[2], "accepted", "Blocs acceptés par CRC"),
        ]:
            image = getattr(trial.reception, view)
            if image is None:
                column.warning("Aucun en-tête fiable : aucune reconstruction.")
            else:
                column.image(image, caption=title, width="stretch")
                column.download_button(
                    "Exporter PNG",
                    png_bytes(image),
                    file_name=view + ".png",
                    mime="image/png",
                    key="image_" + view,
                )
        columns = st.columns(4)
        columns[0].metric("BER pixels", f"{m['payload_ber']:.4g}")
        columns[1].metric("Octets pixels erronés", m["raw_payload_byte_errors"])
        columns[2].metric("Blocs acceptés", f"{m['valid_packets']} / {m['transmitted_packets']}")
        columns[3].metric("Octets effacés", m["erased_bytes"])
        st.info(
            (
                "Magenta = effacement, pas un pixel reçu. La vue diagnostique peut "
                "contenir des blocs au CRC invalide. Aucun en-tête fiable implique aucune "
                "reconstruction depuis l’original."
            )
        )
        st.caption(
            (
                f"État : {m['reconstruction_status']} · Eb/N0 nominal "
                f"transport={m['ebn0_db']:g} dB · M={m['order']} · CP={m['cp_length']} · "
                f"estimation={m['estimation']}. Image déterministe : BER descriptif sans "
                f"IC ; énergie réelle exportée séparément."
            )
        )
        export_rows(dict(settings=result["settings"], rows=[m]), "image_transmission")
    else:
        st.image(original, caption="Image prête à transmettre", width=320)

else:
    st.subheader("Ce que mesure le laboratoire")
    st.markdown("""- **BER** : erreurs binaires / bits observés, avec effectifs et graine exportés.
- **MSE** : erreur quadratique des estimations ; sa réduction n’implique pas toujours un
  meilleur BER.
- **Eb total/N0** : inclut pilotes et CP par bit de données. L’image utilise une référence
  nominale d’alphabet et publie aussi son énergie réelle.
- **CP** : doit couvrir la mémoire du canal pour rendre le modèle diagonal valable. Un CP court
  conserve de l’ISI.
- **ZF / MMSE** : avec le gain de décision pris en compte, mêmes décisions scalaires pour le
  même modèle de canal ; MSE différentes.
- **Pilotes LS** : estimation indépendante par trame et interpolation séparée dans chaque demi-
  bande active.
- **Rayleigh statique** : une réalisation à graine fixée, jamais présentée comme une moyenne
  d’ensemble.
""")
    st.subheader("Périmètre et reproductibilité")
    st.write(
        (
            "Bande de base complexe, timing parfait et CFO nul dans cette interface. "
            "Les expériences de CFO et correction CP restent disponibles dans les "
            "scripts scientifiques. Pas de codage correcteur, retransmission, Doppler "
            "ou équipement RF physique."
        )
    )
    st.write(
        (
            "Les IC BER sont conservateurs à 95 % par ligne, stratifiés par "
            "porteuse/bit. Aucun IC binomial n’est annoncé avec CP insuffisant ou sur "
            "les bits d’une image déterministe. Les segments des courbes ne sont pas "
            "de nouveaux résultats simulés."
        )
    )
    st.write(
        (
            "Une session conserve au plus huit expériences. Les exports CSV/JSON "
            "comprennent les paramètres réellement calculés. Les images chargées ne "
            "sont ni publiées ni ajoutées au dépôt."
        )
    )
    st.link_button("Documentation et expériences", "https://github.com/Gi554/ofdm-lab")

st.divider()
st.caption(
    (
        "OFDM LAB · NumPy / SciPy · résultats simulés, unités normalisées · "
        "laboratoire scientifique et pédagogique"
    )
)
