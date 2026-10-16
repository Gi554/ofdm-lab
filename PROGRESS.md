# Suivi OFDM Lab — 16 octobre 2026

## Bilan de phase 1
Les expériences 1 à 4 sont implémentées, testées et exécutées : génération binaire,
BPSK, QPSK Gray, 16-QAM Gray et 64-QAM Gray. **La phase 1 est validée.**
Les phases 1 à 4 sont validées. La phase 5 est en cours ; les phases 6 et 7 restent à réaliser.

## Livrables
Bibliothèque : génération binaire, validation des bits, modulation/démodulation BPSK et
QPSK Gray, 16-QAM et 64-QAM Gray, visualisation scientifique. Deux configurations JSON ;
six expériences.
Documentation française A–J, théorie, méthode, glossaire, notebook, rapport progressif,
README, licence MIT, pyproject.toml et inventaire de dépendances requirements-lock.txt.
La liste exacte des fichiers livrés est dans docs/file_manifest.txt.

## Tests et qualité
- `python -m pytest -q` dans le venv : **283 tests réussis**, 0 échec.
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
1. Phase 5 : décalage fréquentiel (CFO), estimation et correction.
2. Pilotes, estimation de canal et interpolation, avec comparaison au canal connu.
3. Comparaisons globales avant transmission d’image et interface Streamlit.
Le rapport reste progressif ; les phases 5 à 7 ne sont pas encore validées.

## Organisation du dépôt public
Dépôt : https://github.com/Gi554/ofdm-lab ; branche principale main.
Historique initial séparé : socle, bits, BPSK, QPSK, expériences/documentation, CI.
Tests regroupés par fonctionnalité (33 cas : le test commun des régions de décision
est désormais séparé entre BPSK et QPSK ; couverture scientifique conservée).
Configurations d’assistants, environnements, caches, secrets et journaux locaux exclus.
Identité de commit : compte GitHub du propriétaire, avec adresse noreply.

Validation GitHub du socle : réussie sur Python 3.11, 3.12 et 3.13.
La branche qam-modulations contient un commit 16-QAM, un commit 64-QAM puis
les expériences, résultats et explications. Les journaux locaux ne sont pas publiés.

## Processus Git permanent
Le propriétaire a demandé `staging` pour l’intégration et `main` pour les versions validées.
Chaque fonctionnalité suit commits → PR vers staging → contrôles → merge, puis
PR staging → main → contrôles → merge. Les fusions conservent les commits.
Cette instruction est enregistrée dans AGENTS.md et CONTRIBUTING.md.
La PR QAM #1 a été redirigée vers staging puis fusionnée après contrôles réussis.

## Phase 2 — Premier lot AWGN
Canal additif gaussien complexe implémenté avec N0=Es/(k Eb/N0_lin).
Conversions Eb/N0 → Es/N0 et Es/N0 → SNR avec hypothèses explicites.
71 tests réussis, Ruff et formatage conformes. Les tests statistiques emploient 400 000
échantillons et des tolérances de six erreurs-types sur les moments et corrélations.
Expérience 5 exécutée : 48 000 bits par modulation, 12 cas, Eb/N0=0,6,12 dB.
Écart relatif maximal de puissance : 1,225 %. Pas de renormalisation a posteriori.
Quatre figures, CSV et JSON générés. L’expérience BER/SER reste à réaliser avant validation de phase 2.

## Phase 2 — Bilan final BER/SER
**Phase validée scientifiquement** : expériences 5 et 6 exécutées, 128 tests réussis,
Ruff et formatage conformes. Le lot AWGN est intégré dans main par les PR #4 et #5.
Les métriques et le simulateur AWGN réutilisable ne dupliquent pas les modulateurs.
Le BER QAM exact intègre les transitions gaussiennes, avec contrôle indépendant de la
16-QAM par une formule fermée. L’approximation de plus proches voisins est nommée séparément.

Expérience 6 : 36 points, 1 200 000 bits par point, total 43 200 000 bits ;
Eb/N0 de 0 à 16 dB par pas de 2 ; racine de graine 20261016, NumPy 2.5.4.
- 36/36 références BER dans les IC ponctuels 95 %, 33/36 références SER.
- Toutes les références BER et SER dans l’enveloppe de validation simultanée au moins 99 %.
- Sept points sans erreur binaire : bornes positives, jamais assimilées à Pb=0.
- Les points à moins de 100 erreurs sont signalés ; aucun arrêt adaptatif sur erreurs.
- À 0 dB, approximation QAM inférieure au BER exact de 1,29 % (16-QAM) et 13,46 % (64-QAM).
- Six exports de phase 2 identiques après réexécution avec la même configuration.

CSV : awgn.csv, ber_comparison.csv et awgn_theory.csv. JSON : awgn.json,
ber_comparison.json, ber_summary.json et phase2_reproducibility.json.
Figures : quatre nuages AWGN, courbes BER et SER, écart théorique de l’approximation QAM.
Notebook 02 exécuté cellule par cellule avec Python ; noyau Jupyter interactif non testé.
La dépendance entre erreurs de bits d’un symbole QAM est prise en compte par les IC
simultanés par position. Les modèles restent sans codage, CP, pilotes ou défaut de synchronisation.

## Convention de nommage mise à jour
À la demande du propriétaire, les branches de fonctionnalité portent directement leur nom,
sans préfixe d’outil. Les quatre branches existantes ont été renommées sur GitHub et en local :
awgn-channel, ber-ser-validation, qam-modulations, workflow-staging. Les commits sont conservés.
La règle persistante est mise à jour dans AGENTS.md et CONTRIBUTING.md.
Le processus PR → staging → PR → main, les protections et les merge commits restent applicables.
La phase 2 est fusionnée dans main (PR #7), et sa dernière CI sur main est réussie.

## Phase 3 — FFT/IFFT
Transformées unitaires et fréquences natives implémentées. 144 tests réussis.
Expérience 7 exécutée : inversion, Parseval et orthogonalité ; mesures dans fft.json.
La phase 3 reste en cours : émetteur et récepteur OFDM à développer.

## Phase 3 — Bilan final
Phase validée : expériences 7, 8 et 9 exécutées, 181 tests réussis, Ruff et formatage conformes.
FFT/IFFT unitaires : erreur d’inversion 5,66e-16 et erreur de Gram 5,84e-15 (N=64).
Allocation symétrique, DC et Nyquist nulles, CP 0 à N, réception avec début connu.
Les quatre modulations sont restituées sans erreur sur huit cas idéaux (100 symboles OFDM par cas).
L’expérience AWGN couvre 64 points et 21 632 000 bits ; toutes les références BER et SER
passent l’enveloppe simultanée au moins 99 %. CP=16/N=64 : coût de 0,969100 dB en référence
Eb totale. En référence utile, le CP n’altère pas les performances AWGN.
Neuf exports CSV/JSON identiques après réexécution. Trois figures contrôlées visuellement,
notebook 03 exécuté directement avec Python. Aucun canal multitrajet ni égalisation n’est encore implémenté.
Prochaine phase : démontrer CP et convolution, canal fixe/Rayleigh, égalisation ZF/MMSE.

## Phase 4 — Canal et CP
201 tests réussis. Canal FIR causal complet, réponse fréquentielle non normalisée,
profil Rayleigh normalisé en moyenne. Expériences 10 et 11 réellement exécutées.
Mémoire 6 : écart de diagonalisation 0,0893 sans CP, 0,0457 avec C=3, puis 6,32e-32 avec C>=6.
5 000 canaux Rayleigh : énergie moyenne 1,0044923, écart-type 0,6773086.
Le BER non corrigé reste élevé : le CP ne remplace pas l’égalisation.
La phase 4 reste en cours ; ZF et MMSE sont le lot suivant.

## Phase 4 — Bilan final
Phase validée scientifiquement : expériences 10, 11 et 12, 223 tests réussis.
Convolution complète sur le flux, CP suffisant pour mémoire 6, réponse H non normalisée.
Canaux fixe et Rayleigh statique ; aucune renormalisation des réalisations aléatoires.
Essais d’égalisation : 64 bursts bruités, 10 816 000 bits distincts, 43 264 000 décisions
pour quatre modes appariés. Les essais sans bruit sont séparés dans la synthèse.
Les 128 comparaisons conditionnelles BER/SER passent l’enveloppe globale au moins 99 %.
Les essais sans bruit à CP suffisant sont sans erreur après égalisation connue.
ZF et MMSE à gain pris en compte ont les mêmes comptes d’erreurs ; la MSE MMSE est réduite.
Exemple 16-QAM fixe, CP16, Eb/N0=12 dB : BER brut 0,269611 ; BER égalisé 0,033784 ;
MSE ZF 0,095003, MMSE 0,064693. Les seuils MMSE bruts ont un BER 0,035726, dû au biais.
Les IC sont stratifiés par porteuse/bit sur des trames indépendantes. Aucun IC ni modèle
diagonal n’est appliqué avec CP insuffisant. Les résultats Rayleigh sont conditionnels
à une réalisation fixe, pas des moyennes de BER sur un ensemble de canaux.
Documentation A–J, figures, CSV/JSON et notebook 04 ; exécution notebook directe Python,
mode Jupyter interactif non testé. Estimation imparfaite et CFO restent à la phase 5.

Neuf exports CSV/JSON identiques après réexécution des expériences 10 à 12 (SHA-256).

## Phase 5 — CFO (expérience 13)
Injection CFO continue sur le flux, corrélation CP à début connu et mémoire FIR connue,
correction par fréquence estimée et témoin oracle. Plage modulo 1, pas de CFO entier.
257 tests réussis ; 48 bursts, 3 744 000 bits distincts, 144 mesures appariées.
400 essais supplémentaires pour la RMSE ; 12 cas sans bruit corrigés sans erreur.
AWGN 16-QAM, ε=0,15, Eb utile/N0=24 dB : BER 0,421404 brut, 0,105077 corrigé CP,
0 erreur observée oracle sur 104 000 bits. Le résidu s’accumule sur les 500 trames.
RMSE AWGN de 0,010015 à 0,000810 entre 0 et 18 dB (50 bursts indépendants par point).
Cinq exports CSV/JSON identiques après réexécution ; figure vérifiée visuellement.
Les BER sont descriptifs, sans IC binomial. H reste parfaitement connu pour ZF.
La phase 5 reste en cours : expérience 14 pilotes/interpolation puis 15 comparaison globale.

## Phase 5 — Pilotes et estimation (expérience 14)
Plan en peigne, LS par trame, interpolation linéaire séparée sur les demi-bandes.
Trois comparaisons appariées : aucune correction, H parfait et H estimé, égalisation ZF.
283 tests réussis ; 72 essais, 216 mesures et 3 672 000 bits distincts.
Les 72 moyennes MSE passent l’enveloppe conservatrice Chebyshev + union >=99 %.
Pilotes exclus du BER et du débit utile ; Eb total inclut pilotes et CP, dont le coût
pilote cohérent est calculé exactement. Pas 4 : 16 pilotes, 36 données, facteur 1,827144.
16-QAM fixe, pas 4, Eb total/N0=18 dB : BER non corrigé 0,268792 ; parfait 0,018222 ;
estimé 0,144833. MSE estimée 0,130398 contre espérance 0,130950 : biais d’interpolation.
Quatre exports CSV/JSON reproductibles ; figure vérifiée visuellement et notebook 06
exécuté directement avec Python (mode Jupyter interactif non testé).
La phase 5 reste en cours : expérience 15 de comparaison globale à réaliser.
