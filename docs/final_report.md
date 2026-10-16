# Conception, simulation et analyse des performances d’un système de transmission numérique OFDM sur canaux AWGN et multitrajets

**Rapport progressif — phases 1 à 4 validées ; phases 5 à 7 à réaliser.**

## 1. Résumé
Une bibliothèque NumPy implémente la génération binaire, la BPSK, la QPSK Gray et les QAM Gray 16/64.
Le canal AWGN, les compteurs BER/SER et les références exactes complètent ce socle.
Les résultats détaillés des phases 1 et 2 sont référencés dans PROGRESS.md et les mesures JSON.
## 2. Introduction générale
L’objectif est de construire une chaîne OFDM reproductible, en privilégiant sa validation.
## 3. Contexte des communications numériques
L’information binaire est regroupée en symboles complexes. Aucun matériel RF n’est requis.
## 4. Principes des modulations numériques
Voir theory/01_modulations.md et theory/02_qam.md pour les mappings, décisions et normalisations.
## 5. Fondements mathématiques de l’OFDM
DFT unitaire et orthogonalité vérifiées : voir theory/05_fft_ofdm.md.
N=64, Δf=15 kHz, Fs=960 kHz ; erreur d’inversion mesurée 5,66e-16.
## 6. Modélisation des canaux radio
AWGN complexe disponible : E|n|²=N0 et N0/2 par axe. Expérience 5 : 12 cas,
écart relatif maximal de puissance 1,225 %. Voir theory/03_awgn.md et experiments/05_awgn.md.
Canal FIR causal complet et Rayleigh statique disponibles. Le CP couvrant la mémoire 6
ramène l’erreur de diagonalisation de 0,0893 à 6,32e-32 sans bruit.
## 7. Architecture de l’émetteur
Les mappings BPSK/QPSK/16-QAM/64-QAM sont disponibles. Allocation symétrique sans DC/Nyquist, IFFT unitaire et copie cyclique implémentées.
## 8. Architecture du récepteur
Les décisions cohérentes idéales sont disponibles ; le récepteur OFDM à début connu retire le CP, applique la FFT et extrait les données.
## 9. Méthodologie expérimentale
Voir methodology.md : graine fixe, sorties traçables et validation déterministe.
## 10. Résultats des simulations
Sur 10 000 bits (graine 20261016), 0 erreur BPSK et 0 erreur QPSK en canal idéal ;
énergie moyenne Es=1 dans les deux cas. Les 223 tests passent. Six exports CSV/JSON
sont identiques après réexécution. Consulter results/reports pour les mesures détaillées.
Sur 120 000 bits QAM, aucune erreur binaire ou symbole en canal idéal. Distances minimales
mesurées : 0,632456 (16-QAM) et 0,308607 (64-QAM). L’énergie moyenne de chaque alphabet
est 1 ; celles des tirages sont 1,00264 et 1,007333. Quatre exports QAM sont identiques
après réexécution. Voir experiments/04_qam.md pour la méthode et les figures.
## 11. Analyse des performances BER
Les quatre modulations ont été simulées sur AWGN pour 36 points, soit 43 200 000 bits.
À Eb/N0=6 dB, BER BPSK=0,0024225 (2 907 erreurs) et QPSK=0,00246833 (2 962 erreurs),
chacun sur 1 200 000 bits ; référence commune 0,002388291. Les BER QAM mesurés valent
0,0281733 en 16-QAM et 0,0835975 en 64-QAM. Les données intégrales, effectifs et IC sont
dans results/datasets/ber_comparison.csv.
36/36 références BER et 33/36 références SER sont dans leurs IC ponctuels 95 %. Toutes
sont dans l’enveloppe simultanée 99 %. Ces exclusions ponctuelles sont compatibles avec
le risque statistique, sans modification des graines ni des résultats.
Voir experiments/06_ber_comparison.md et theory/04_ber_ser.md pour les hypothèses,
les bornes après zéro erreur, et le traitement des dépendances binaires QAM.
## 12. Étude de l’égalisation et de l’estimation de canal
Égalisation ZF et MMSE connue validée sur 64 essais appariés, 10,816 millions de bits.
Les 128 comparaisons BER/SER conditionnelles passent l’enveloppe simultanée 99 %.
En 16-QAM fixe à 12 dB, BER brut 0,269611 contre 0,033784 égalisé. Le MMSE réduit
la MSE de 0,095003 à 0,064693 ; à seuils adaptés, ses décisions scalaires sont celles de ZF.
Les seuils non adaptés conservent un biais QAM. Les IC tiennent compte des différences
entre porteuses et positions binaires ; aucun IC binomial n’est annoncé avec CP court.
Le canal est parfaitement connu ; son estimation reste à la phase 5.
## 13. Application à la transmission d’image
Non réalisée.
## 14. Limites du modèle
AWGN idéal disponible ; canal multitrajet statique disponible, sans Doppler, de mise en forme, de codage
ni de défaut de synchronisation. Les événements très rares sont peu résolus par l’effectif fixe ; les IC le signalent.
## 15. Perspectives : MIMO-OFDM, 5G NR et radio logicielle
Extensions ultérieures ; aucune conformité à une norme n’est revendiquée.
## 16. Conclusion générale
Les fondations de mapping sont le premier jalon ; la chaîne complète reste à réaliser.
## 17. Bibliographie
NumPy, documentation officielle : [Random Generator](https://numpy.org/doc/stable/reference/random/generator.html) et [Compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html), consultées le 16 octobre 2026.
David Tse et Pramod Viswanath, *Fundamentals of Wireless Communication*, Cambridge University Press, 2005.
[Page officielle des auteurs](https://web.stanford.edu/~dntse/wireless_book.html),
appendice A consacré à la détection et à l’estimation en bruit gaussien ; référence vérifiée le 16 octobre 2026.
Les équations du premier lot sont explicitées intégralement dans la documentation théorique.
[SciPy : méthode Clopper–Pearson](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html),
documentation officielle vérifiée le 16 octobre 2026.
## 18. Annexes techniques
Code : src/ofdm_lab ; configuration : configs/fundamentals.json ; tests : tests/.

### Complément phase 3
21 632 000 bits OFDM sur AWGN, 64 points, quatre modulations, CP 0/16 et deux références Eb.
Toutes les références BER/SER passent la validation simultanée 99 %. Les huit essais idéaux
sont sans erreur. La moyenne mesurée d’énergie totale de l’expérience 8 vaut 65,67047 contre
65 attendue : fluctuation d’un tirage fini sans renormalisation artificielle.
Les résultats détaillés et hypothèses sont dans experiments/08_ofdm_transmitter.md et
experiments/09_ofdm_awgn.md. Le modèle ne démontre pas encore le rôle du CP en multitrajet.

### Complément phase 4
Les expériences de convolution, de statistiques Rayleigh et d’égalisation sont documentées
séparément dans experiments/10_cyclic_prefix.md, 11_multipath_channel.md et 12_channel_equalization.md.
Les références de la réalisation Rayleigh sont conditionnelles ; aucune moyenne d’ensemble
BER Rayleigh n’est revendiquée. La connaissance parfaite de H précède volontairement son estimation.

## Expérience 13 — Première synchronisation fréquentielle
Le CFO est appliqué sans remise à zéro de phase sur les symboles. La correction CP
restitue les 12 cas sans bruit testés. Sous bruit, elle réduit souvent le BER mais
l’erreur résiduelle accumulée sur un long burst peut rester importante, même à CFO nul.
L’oracle corrige avec le CFO réel ; il constitue un témoin, pas une méthode pratique.
3 744 000 bits distincts, 48 bursts, 144 mesures et 400 essais de RMSE documentés dans
[l’expérience 13](experiments/13_frequency_offset.md). La capture est modulo 1 et
nécessite un début et une mémoire connus. Pas encore de pilotes ni d’estimation de H.

## Expérience 14 — Canal estimé par pilotes
Pilotes en peigne, LS et interpolation linéaire par demi-bande implémentés, en réutilisant
mapping, FFT/CP, égalisation et décisions. 72 essais et 3 672 000 bits distincts
comparent les modes non corrigé, H parfait et H estimé.
Le bilan Eb total inclut le coût pilote et le CP déterministe ; la MSE sépare biais
et bruit avec une référence analytique. L’interpolation conserve un plancher sur les
canaux très sélectifs : H estimé ne remplace pas le témoin parfait.
Voir [l’expérience 14](experiments/14_channel_estimation.md) pour mesures et limites.
La comparaison globale, l’image et l’interface restent à développer.
