# Suivi OFDM Lab — 16 octobre 2026

## Bilan de phase 1
Les expériences 1 à 4 sont implémentées, testées et exécutées : génération binaire,
BPSK, QPSK Gray, 16-QAM Gray et 64-QAM Gray. **La phase 1 est validée.**
Les phases 2 à 7 ne sont pas encore réalisées.

## Livrables
Bibliothèque : génération binaire, validation des bits, modulation/démodulation BPSK et
QPSK Gray, 16-QAM et 64-QAM Gray, visualisation scientifique. Deux configurations JSON ;
quatre expériences.
Documentation française A–J, théorie, méthode, glossaire, notebook, rapport progressif,
README, licence MIT, pyproject.toml et inventaire de dépendances requirements-lock.txt.
La liste exacte des fichiers livrés est dans docs/file_manifest.txt.

## Tests et qualité
- `python -m pytest -q` dans le venv : **51 tests réussis**, 0 échec (0,63 s lors de la dernière exécution locale).
- `python -m ruff check .` : **All checks passed!**
- Mapping/démapping de 100 000 bits par modulation, énergie Es=1, Gray et voisinage,
  dimensions, seuils de décision, entrées invalides et isolation du générateur global.
- Syntaxe Python et cellules du notebook vérifiées.
- Notebook : cellule exécutée directement avec Python, sorties enregistrées ; lancement par
  un noyau Jupyter interactif non testé.
- Réexécution des trois scripts : **6 fichiers CSV/JSON identiques** (SHA-256).
- Cinq PNG contrôlés visuellement : axes, annotations et légendes lisibles.
- Alphabets QAM exhaustifs, voisins Gray, comparaison à un détecteur euclidien indépendant.
- Réexécution QAM : **4 exports CSV/JSON identiques** (SHA-256).

## Mesures réellement obtenues
Graine 20261016, NumPy 2.5.4, 10 000 bits par expérience.

| Expérience | Symboles | Erreurs binaires | BER observé | Énergie moyenne Es |
|---|---:|---:|---:|---:|
| BPSK idéale | 10 000 | 0 | 0 | 1,0 |
| QPSK Gray idéale | 5 000 | 0 | 0 | 1,0 |

Génération binaire : 5 000 bits à 1, fraction observée 0,5. Cette égalité est fortuite ;
le générateur n’impose pas un nombre égal de 0 et de 1.
La restitution exacte valide l’inversion du mapping ; elle ne prouve aucune probabilité
d’erreur nulle sur un canal bruité. Les symboles idéaux sont les seuls tracés à ce stade.

## Résultats disponibles
- results/figures : 01_binary_generation.png, 02_bpsk.png, 03_qpsk.png.
- results/datasets : binary_generation.csv, bpsk.csv, qpsk.csv.
- results/reports : binary_generation.json, bpsk.json, qpsk.json,
  reproducibility.json, pytest.txt, ruff.txt.

## Commandes et environnement
Voir docs/commands.md et docs/environment.md. Python 3.12.14, package installé en mode
éditable dans .venv. Les journaux d’installation propres à la machine sont conservés
localement et exclus du dépôt public. Aucun résultat scientifique n’a été inventé.

## Bilan QAM — expérience 4
Graine 20261016, NumPy 2.5.4, 120 000 bits par modulation, canal idéal.

| Modulation | Symboles | Erreurs bits / symboles | Es alphabet | Es tirage | Distance minimale |
|---|---:|---:|---:|---:|---:|
| 16-QAM | 30 000 | 0 / 0 | 1 | 1,00264 | 0,632456 |
| 64-QAM | 20 000 | 0 / 0 | ≈1 | 1,007333 | 0,308607 |

La moyenne sur un tirage fini peut différer de 1 ; aucune renormalisation ad hoc du tirage
n’est appliquée. La 64-QAM rapproche les points à Es constant. La restitution idéale ne
quantifie pas le BER sous bruit. Les défauts de synchronisation et le canal restent exclus.
Sorties : 04_16qam.png, 04_64qam.png, alphabets CSV, qam_comparison.csv,
qam.json et qam_reproducibility.json. Documentation : docs/experiments/04_qam.md.

## Prochaines étapes
1. Phase 2 : ajouter AWGN et les conventions précises Eb/N0–Es/N0–SNR.
2. Ajouter BER/SER, intervalles binomiaux et référence théorique BPSK/QPSK.
3. Comparer les quatre modulations avec des effectifs statistiquement adaptés.
4. Poursuivre FFT/IFFT, OFDM et préfixe cyclique dans l’ordre imposé.
Interface Streamlit différée à la phase 7 ; rapport final encore progressif.

## Organisation du dépôt public
Dépôt : https://github.com/Gi554/ofdm-lab ; branche principale main.
Historique initial séparé : socle, bits, BPSK, QPSK, expériences/documentation, CI.
Tests regroupés par fonctionnalité (33 cas : le test commun des régions de décision
est désormais séparé entre BPSK et QPSK ; couverture scientifique conservée).
Configurations d’assistants, environnements, caches, secrets et journaux locaux exclus.
Identité de commit : compte GitHub du propriétaire, avec adresse noreply.

Validation GitHub du socle : réussie sur Python 3.11, 3.12 et 3.13.
La branche codex/qam-modulations contient un commit 16-QAM, un commit 64-QAM puis
les expériences, résultats et explications. Les journaux locaux ne sont pas publiés.
