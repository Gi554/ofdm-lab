# OFDM Lab

[![Validation](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml)

Laboratoire scientifique et pédagogique de transmissions numériques, niveau L3 avancée / Master.
Implémentations explicites avec NumPy, en bande de base complexe, sans équipement radio externe.

## État du projet

La phase 1 est validée : génération binaire, BPSK, QPSK Gray, 16-QAM et 64-QAM Gray.
La phase 2 est validée : AWGN, conversions énergétiques, BER/SER, intervalles de confiance
et références théoriques exactes. **128 tests** ; courbes sur **43,2 millions de bits**.
OFDM, multitrajets, synchronisation, image et interface restent à développer.
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
.\.venv\Scripts\python.exe experiments/05_awgn.py
.\.venv\Scripts\python.exe experiments/06_ber_comparison.py
```

Les scripts lisent les configurations de `configs/` et écrasent leurs résultats dans `results/` :
figures PNG, données CSV et mesures JSON. La graine fixe vaut 20261016 : 10 000 bits pour les expériences 1–3,
120 000 bits pour la comparaison QAM (`configs/qam.json`), 48 000 bits pour les nuages AWGN,
et 1 200 000 bits par point BER/SER (`configs/ber.json`, 36 points).
La reproductibilité bit à bit doit être vérifiée avec la même version NumPy ; sa version
est enregistrée dans chaque mesure. Les résultats sont ceux d’un modèle discret, sans chaîne RF physique.

## Conventions scientifiques

QAM : bits I puis Q, poids fort en tête ; alphabets Gray normalisés à Es=1.
Voir [les conventions QAM](docs/theory/02_qam.md).

BPSK : 0 → +1, 1 → −1. QPSK : (bI,bQ) → ((1−2bI)+j(1−2bQ))/√2.
Énergie moyenne Es = 1 ; Eb = Es/k avec k = 1, 2, 4 ou 6. Synchronisation et phase parfaites.
En BPSK/QPSK, le seuil nul choisit le bit 0 ; en QAM, une égalité choisit le niveau
d’amplitude supérieur. Les longueurs non multiples de k sont refusées sans bourrage implicite.
AWGN : variance complexe N0=Es/(k Eb/N0_lin), N0/2 par axe. Ni CP ni pilotes.
Les IC BER respectent la dépendance entre positions binaires QAM. Zéro erreur est
accompagné d’une borne supérieure. Aucune fréquence d’échantillonnage ni aucun débit physique
ne sont imposés à ce stade. Voir [la méthodologie BER/SER](docs/theory/04_ber_ser.md).

## Organisation

- `src/ofdm_lab/` : bibliothèque réutilisable, validation des entrées et visualisation.
- `experiments/`, `configs/` : scripts et paramètres des expériences exécutables.
- `tests/` : mapping, Gray, énergie, dimensions, entrées invalides et restitution.
- `docs/` : théorie, méthode, explications et rapport progressif en français.
- `notebooks/` : démonstration pédagogique utilisant directement la bibliothèque.
- `results/` : sorties réellement calculées ; `app/` réservé à la phase 7.

Licence MIT. Aucun algorithme de chaîne OFDM fourni par une bibliothèque externe.

## Processus de développement

`codex/<fonctionnalite>` → PR → **staging** → PR → **main**.
Les deux PR sont fusionnées après réussite des contrôles, avec des merge commits qui
conservent les commits par fonctionnalité. `main` reste la branche par défaut.
Voir [CONTRIBUTING.md](CONTRIBUTING.md) et [AGENTS.md](AGENTS.md).

## Simulation réutilisable

```python
from ofdm_lab.simulation import simulate_awgn

result = simulate_awgn(order=16, ebn0_db=6, n_bits=120_000, seed=42)
print(result["bit_errors"], result["n_bits"], result["ber"])
print(result["ber_ci_lower"], result["ber_ci_upper"], result["ber_theory_exact"])
```

L’effectif est fixé avant le tirage ; les blocs limitent la mémoire. La taille des blocs,
la graine et la version NumPy font partie des paramètres de reproduction.
