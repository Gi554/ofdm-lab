# OFDM Lab

[![Validation](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Gi554/ofdm-lab/actions/workflows/ci.yml)

Laboratoire scientifique et pédagogique de transmissions numériques, niveau L3 avancée / Master.
Implémentations explicites avec NumPy, en bande de base complexe, sans équipement radio externe.

## État du projet

La phase 1 est validée : génération binaire, BPSK, QPSK Gray, 16-QAM et 64-QAM Gray.
La phase 2 est validée : AWGN, conversions énergétiques, BER/SER, intervalles de confiance
et références théoriques exactes. **293 tests** ; courbes sur **43,2 millions de bits**.
La phase 3 est validée : FFT/IFFT unitaires, émetteur/récepteur OFDM, CP, DC/gardes nulles,
validation AWGN sur 21,632 millions de bits. La phase 4 est validée : canal multitrajet, CP et égalisation connue ZF/MMSE.
La phase 5 est validée : CFO et correction CP, pilotes LS/interpolation, comparaison globale.
Transmission d’image (phase 6) et interface Streamlit (phase 7) restent à développer.
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
.\.venv\Scripts\python.exe experiments/07_fft_ifft.py
.\.venv\Scripts\python.exe experiments/08_ofdm_transmitter.py
.\.venv\Scripts\python.exe experiments/09_ofdm_awgn.py
.\.venv\Scripts\python.exe experiments/10_cyclic_prefix.py
.\.venv\Scripts\python.exe experiments/11_multipath_channel.py
.\.venv\Scripts\python.exe experiments/12_channel_equalization.py
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

`<fonctionnalite>` → PR → **staging** → PR → **main**.
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

## Chaîne OFDM

```python
from ofdm_lab import generate_bits
from ofdm_lab.configuration import OFDMConfig
from ofdm_lab.transmitter import transmit
from ofdm_lab.receiver import receive

config = OFDMConfig(n_fft=64, n_active=52, cp_length=16, order=4)
bits = generate_bits(100 * config.bits_per_ofdm_symbol, seed=42)
received_bits = receive(transmit(bits, config).waveform, config).bits
```

Les blocs doivent être complets ; début et configuration sont connus.
`ofdm_simulation.simulate_ofdm_awgn` utilise `reference="useful"` ou `"total"`
pour inclure explicitement le coût du CP dans Eb. Voir docs/theory/05_fft_ofdm.md.

## Canal connu et égalisation

`channels.apply_multipath` conserve la convolution complète. Le récepteur reçoit explicitement
le burst attendu et `channel_response=H`, calculé par `channels.frequency_response`.
Choisir `equalizer="zf"` ou `"mmse"` ; le mode MMSE par défaut prend son gain résiduel
en compte pour les décisions. Les effets du CP et les IC conditionnels sont documentés dans
[la note d’égalisation](docs/theory/07_equalization.md). Le canal n’est pas encore estimé.

### Synchronisation — phase 5 validée
L’expérience 13 ajoute un CFO continu et une première correction par corrélation CP,
avec timing et mémoire connus. Comparaison brute/estimée/oracle, ICI et RMSE.
Les limites de capture modulo 1 et de dérive résiduelle sont mesurées explicitement.
Voir [l’expérience](docs/experiments/13_frequency_offset.md). Pilotes et interpolation sont décrits dans l’expérience 14 ci-dessous.

### Estimation du canal par pilotes
L’expérience 14 ajoute des pilotes en peigne et une estimation LS avec interpolation
linéaire par trame. Elle compare canal connu, estimé et non corrigé, avec BER utile,
MSE analytique et mesurée, coût des pilotes et débit. Voir
[l’expérience 14](docs/experiments/14_channel_estimation.md).
La comparaison globale est disponible dans [l’expérience 15](docs/experiments/15_global_comparison.md).

### Comparaison globale
192 essais couvrent quatre modulations, deux FFT, deux CP, deux densités de pilotes,
deux niveaux Eb/N0 et trois canaux. Cinq modes appariés ; 4 832 256 bits distincts.
Les 128 références BER valides passent une enveloppe simultanée au moins 99 %.
Les résultats à CP insuffisant sont descriptifs. La phase 5 est terminée.
