# Conception, simulation et analyse des performances d’un système de transmission numérique OFDM sur canaux AWGN et multitrajets

**Rapport progressif — seul le premier lot de la phase 1 est disponible.**

## 1. Résumé
Une bibliothèque NumPy implémente la génération binaire, la BPSK et la QPSK Gray.
Les résultats détaillés du lot sont référencés dans PROGRESS.md et les mesures JSON.
## 2. Introduction générale
L’objectif est de construire une chaîne OFDM reproductible, en privilégiant sa validation.
## 3. Contexte des communications numériques
L’information binaire est regroupée en symboles complexes. Aucun matériel RF n’est requis.
## 4. Principes des modulations numériques
Voir theory/01_modulations.md pour les mappings, décisions et normalisations.
## 5. Fondements mathématiques de l’OFDM
À rédiger après expérience 7.
## 6. Modélisation des canaux radio
À réaliser : AWGN puis convolution multitrajet.
## 7. Architecture de l’émetteur
Le mapping BPSK/QPSK est disponible. Allocation, IFFT et CP restent à développer.
## 8. Architecture du récepteur
Les décisions cohérentes idéales sont disponibles ; le récepteur OFDM reste à développer.
## 9. Méthodologie expérimentale
Voir methodology.md : graine fixe, sorties traçables et validation déterministe.
## 10. Résultats des simulations
Sur 10 000 bits (graine 20261016), 0 erreur BPSK et 0 erreur QPSK en canal idéal ;
énergie moyenne Es=1 dans les deux cas. Les 33 tests passent. Six exports CSV/JSON
sont identiques après réexécution. Consulter results/reports pour les mesures détaillées.
## 11. Analyse des performances BER
La restitution idéale ne mesure pas une performance sous AWGN ; étude à venir.
## 12. Étude de l’égalisation et de l’estimation de canal
Non réalisée.
## 13. Application à la transmission d’image
Non réalisée.
## 14. Limites du modèle
Pas de bruit, de canal radio, de mise en forme, de codage ni de défaut de synchronisation.
## 15. Perspectives : MIMO-OFDM, 5G NR et radio logicielle
Extensions ultérieures ; aucune conformité à une norme n’est revendiquée.
## 16. Conclusion générale
Les fondations de mapping sont le premier jalon ; la chaîne complète reste à réaliser.
## 17. Bibliographie
NumPy, documentation officielle : [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html) et [Compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html), consultées le 16 octobre 2026.
Les références de communications numériques seront ajoutées avec les phases correspondantes.
Les équations du premier lot sont explicitées intégralement dans la documentation théorique.
## 18. Annexes techniques
Code : src/ofdm_lab ; configuration : configs/fundamentals.json ; tests : tests/.
