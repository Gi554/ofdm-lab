# OFDM Lab

[![Validation](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml)

Laboratoire scientifique et pédagogique de transmissions numériques, niveau L3 avancée / Master.
Implémentations explicites avec NumPy, en bande de base complexe, sans équipement radio externe.

## État du projet

La phase 1 est validée : génération binaire, BPSK, QPSK Gray, 16-QAM et 64-QAM Gray.
Les phases AWGN, OFDM, multitrajets, synchronisation, image et interface restent à développer.
Voir [PROGRESS.md](PROGRESS.md) pour les mesures et validations exécutées.

## Installation (PowerShell, Python 3.11 ou ultérieur)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

L’activation du venv n’est pas nécessaire. Sous Linux/macOS, utiliser `.venv/bin/python`.
L’interface Streamlit reste optionnelle : `python -m pip install -e ".[app]"`.
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les conventions de commits et de validation.

## Expériences reproductibles

```powershell
.\.venv\Scripts\python.exe experiments/01_binary_generation.py
.\.venv\Scripts\python.exe experiments/02_bpsk.py
.\.venv\Scripts\python.exe experiments/03_qpsk.py
.\.venv\Scripts\python.exe experiments/04_qam.py
```

Les scripts lisent `configs/fundamentals.json` et écrasent leurs résultats dans `results/` :
figures PNG, données CSV et mesures JSON. La graine fixe vaut 20261016 : 10 000 bits pour les expériences 1–3,
120 000 bits pour la comparaison QAM (`configs/qam.json`).
La reproductibilité bit à bit doit être vérifiée avec la même version NumPy ; sa version
est enregistrée dans chaque mesure. Aucun résultat radio n’est déduit de ces essais idéaux.

## Conventions scientifiques

QAM : bits I puis Q, poids fort en tête ; alphabets Gray normalisés à Es=1.
Voir [les conventions QAM](docs/theory/02_qam.md).

BPSK : 0 → +1, 1 → −1. QPSK : (bI,bQ) → ((1−2bI)+j(1−2bQ))/√2.
Énergie moyenne Es = 1 ; Eb = Es/k avec k = 1 ou 2. Synchronisation et phase parfaites.
Les décisions sur les frontières choisissent le bit 0. La QPSK refuse une longueur impaire.
Pas de bruit, de fréquence d’échantillonnage ni de débit physique imposés à ce stade.

## Organisation

- `src/ofdm_lab/` : bibliothèque réutilisable, validation des entrées et visualisation.
- `experiments/`, `configs/` : scripts et paramètres des expériences exécutables.
- `tests/` : mapping, Gray, énergie, dimensions, entrées invalides et restitution.
- `docs/` : théorie, méthode, explications et rapport progressif en français.
- `notebooks/` : démonstration pédagogique utilisant directement la bibliothèque.
- `results/` : sorties réellement calculées ; `app/` réservé à la phase 7.

Licence MIT. Aucun algorithme de chaîne OFDM fourni par une bibliothèque externe.
