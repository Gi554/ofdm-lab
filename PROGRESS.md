# Suivi OFDM Lab — 16 octobre 2026

## Bilan du lot de démarrage
Expériences 1, 2 et 3 implémentées, testées et exécutées. Le premier lot est validé.
La phase 1 entière reste ouverte : 16-QAM et 64-QAM (expérience 4) à développer.
Aucune phase suivante n’est déclarée terminée.

## Livrables
Bibliothèque : génération binaire, validation des bits, modulation/démodulation BPSK et
QPSK Gray, visualisation scientifique. Configuration JSON centralisée ; trois expériences.
Documentation française A–J, théorie, méthode, glossaire, notebook, rapport progressif,
README, licence MIT, pyproject.toml et inventaire de dépendances requirements-lock.txt.
La liste exacte des fichiers livrés est dans docs/file_manifest.txt.

## Tests et qualité
- `python -m pytest -q` dans le venv : **33 tests réussis**, 0 échec.
- `python -m ruff check .` : **All checks passed!**
- Mapping/démapping de 100 000 bits par modulation, énergie Es=1, Gray et voisinage,
  dimensions, seuils de décision, entrées invalides et isolation du générateur global.
- Syntaxe Python et cellules du notebook vérifiées.
- Notebook : cellule exécutée directement avec Python, sorties enregistrées ; lancement par
  un noyau Jupyter interactif non testé.
- Réexécution des trois scripts : **6 fichiers CSV/JSON identiques** (SHA-256).
- Trois PNG contrôlés visuellement : axes, annotations et légendes lisibles.

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

## Prochaines étapes
1. Implémenter 16-QAM et 64-QAM Gray ; tester tout l’alphabet et sa normalisation.
2. Terminer et valider la phase 1.
3. Ajouter AWGN, métriques BER/SER, conversions Eb/N0–Es/N0–SNR et intervalles binomiaux.
4. Poursuivre FFT/IFFT, OFDM et préfixe cyclique dans l’ordre imposé.
Interface Streamlit différée à la phase 7 ; rapport final encore progressif.

## Organisation du dépôt public
Dépôt : https://github.com/Gi554/ofdm-lab ; branche principale main.
Historique initial séparé : socle, bits, BPSK, QPSK, expériences/documentation, CI.
Tests regroupés par fonctionnalité (33 cas : le test commun des régions de décision
est désormais séparé entre BPSK et QPSK ; couverture scientifique conservée).
Configurations d’assistants, environnements, caches, secrets et journaux locaux exclus.
Identité de commit : compte GitHub du propriétaire, avec adresse noreply.
