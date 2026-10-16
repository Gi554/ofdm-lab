# CAHIER DES CHARGES — OFDM LAB
## Laboratoire scientifique de simulation des transmissions numériques

**Niveau cible :** Licence 3 avancée / Master en télécommunications
**Langage principal :** Python
**Nature :** Projet scientifique, pédagogique et expérimental
**Objectif :** Construire, tester, analyser et documenter une chaîne complète de transmission numérique OFDM.

---

# 1. RÔLE DE CODEX

Tu es un ingénieur senior spécialisé en télécommunications numériques, traitement du signal, communications sans fil et développement scientifique Python.

Ta mission est de développer intégralement un projet nommé **OFDM Lab**.

Ce projet doit être un véritable laboratoire de simulation, et non une simple démonstration graphique.

Tu dois :

- Implémenter les algorithmes de transmission numérique.
- Expliquer les principes mathématiques et physiques.
- Construire progressivement une chaîne OFDM complète.
- Produire des expériences reproductibles.
- Générer des graphiques scientifiques exploitables.
- Comparer les résultats expérimentaux aux modèles théoriques.
- Écrire des tests automatisés.
- Documenter chaque module et chaque expérience en français.
- Créer une interface interactive uniquement après validation du moteur scientifique.
- Produire un rapport scientifique final.

**Règle fondamentale :** ne jamais privilégier une belle interface au détriment de la validité scientifique.

# 2. OBJECTIFS SCIENTIFIQUES

À la fin du projet, le laboratoire doit permettre de :

1. Générer des séquences binaires pseudo-aléatoires.
2. Moduler et démoduler les bits en BPSK, QPSK, 16-QAM et 64-QAM.
3. Visualiser les constellations idéales et bruitées.
4. Simuler un canal AWGN.
5. Calculer le rapport signal/bruit, Eb/N0 et Es/N0.
6. Mesurer le taux d'erreurs binaires (BER) et le taux d'erreurs de symboles (SER).
7. Comparer les performances expérimentales aux expressions théoriques.
8. Implémenter la transformation FFT et IFFT.
9. Construire un émetteur OFDM.
10. Ajouter un préfixe cyclique.
11. Simuler des canaux radio à trajets multiples.
12. Construire un récepteur OFDM.
13. Implémenter l'estimation de canal et l'égalisation.
14. Étudier l'influence des interférences et du décalage fréquentiel.
15. Comparer les performances des différentes configurations.
16. Transmettre et reconstruire une image à travers un canal simulé.
17. Visualiser les signaux dans les domaines temporel et fréquentiel.
18. Disposer d'une interface permettant de réaliser des expériences personnalisées.

Le projet doit rester entièrement réalisable sans équipement radio externe.

# 3. ENVIRONNEMENT TECHNIQUE

Utiliser :

- Python 3.11 ou version compatible récente.
- NumPy pour les calculs numériques.
- SciPy pour le traitement du signal.
- Matplotlib pour les visualisations scientifiques.
- Pandas pour les résultats expérimentaux.
- Pytest pour les tests.
- Streamlit pour l'interface finale.
- Jupyter Notebook pour les démonstrations pédagogiques.
- Ruff pour la qualité du code.

GNU Radio pourra être proposé ultérieurement, mais ne doit pas être une dépendance obligatoire.

Utiliser un environnement virtuel Python et un fichier `pyproject.toml` pour gérer le projet.

# 4. ARCHITECTURE DU PROJET

Créer l'organisation suivante :

```text
ofdm-lab/
├── src/
│   └── ofdm_lab/
│       ├── __init__.py
│       ├── bits.py
│       ├── modulation.py
│       ├── demodulation.py
│       ├── noise.py
│       ├── channels.py
│       ├── transforms.py
│       ├── transmitter.py
│       ├── receiver.py
│       ├── synchronization.py
│       ├── estimation.py
│       ├── equalization.py
│       ├── metrics.py
│       ├── visualization.py
│       ├── image_transmission.py
│       └── configuration.py
├── experiments/
│   ├── 01_binary_generation.py
│   ├── 02_bpsk.py
│   ├── 03_qpsk.py
│   ├── 04_qam.py
│   ├── 05_awgn.py
│   ├── 06_ber_comparison.py
│   ├── 07_fft_ifft.py
│   ├── 08_ofdm_transmitter.py
│   ├── 09_ofdm_awgn.py
│   ├── 10_cyclic_prefix.py
│   ├── 11_multipath_channel.py
│   ├── 12_channel_equalization.py
│   ├── 13_frequency_offset.py
│   ├── 14_channel_estimation.py
│   ├── 15_modulation_comparison.py
│   ├── 16_image_transmission.py
│   └── 17_complete_system.py
├── notebooks/
├── tests/
├── docs/
│   ├── theory/
│   ├── experiments/
│   ├── methodology.md
│   ├── glossary.md
│   └── final_report.md
├── results/
│   ├── figures/
│   ├── datasets/
│   └── reports/
├── app/
│   └── streamlit_app.py
├── pyproject.toml
├── README.md
└── LICENSE
```

L'architecture peut être adaptée si une meilleure organisation est justifiée.

# 5. PLAN DE DÉVELOPPEMENT

## PHASE 1 — Fondamentaux de la transmission numérique

### Expérience 1 : génération binaire

Créer un générateur de bits pseudo-aléatoires.

Étudier :
- La représentation binaire de l'information.
- Les notions de bit, symbole et débit binaire.
- Le caractère pseudo-aléatoire des séquences.
- La reproductibilité avec une graine aléatoire.

Produire une visualisation de la séquence.

### Expérience 2 : modulation BPSK

Implémenter :

- Le mapping binaire vers les symboles BPSK.
- La démodulation cohérente.
- La constellation BPSK.
- Le calcul de l'énergie moyenne.

Présenter les équations mathématiques.

### Expérience 3 : modulation QPSK

Implémenter :

- Le regroupement des bits par paires.
- Le mapping Gray.
- La représentation complexe I/Q.
- La normalisation énergétique.
- La démodulation.

Expliquer pourquoi la QPSK transporte deux bits par symbole.

### Expérience 4 : modulations QAM

Implémenter la 16-QAM et la 64-QAM.

Expliquer :
- La modulation d'amplitude en quadrature.
- La distance entre les points.
- L'efficacité spectrale.
- Le compromis entre débit et robustesse.

Comparer les constellations.

**Validation de phase :** chaque modulateur doit pouvoir restituer exactement les bits transmis en l'absence de bruit.

---

## PHASE 2 — Bruit et performances

### Expérience 5 : canal AWGN

Implémenter :

y = x + n

où n est un bruit gaussien complexe circulaire.

Étudier :
- Le bruit thermique.
- La variance du bruit.
- Le rapport signal/bruit.
- La dispersion des constellations.

### Expérience 6 : courbes BER

Pour chaque modulation :

- Générer suffisamment de bits.
- Ajouter du bruit pour différentes valeurs de Eb/N0.
- Démoduler les symboles.
- Compter les erreurs.
- Calculer BER et SER.
- Comparer les résultats aux expressions théoriques applicables.

Pour la BPSK et la QPSK Gray cohérentes sur AWGN, utiliser notamment :

BER = Q(sqrt(2 × Eb/N0))

Documenter la fonction Q.

Pour les modulations QAM, préciser lorsqu'une formule théorique est approximative.

**Exigences scientifiques :**

Distinguer correctement Eb/N0, Es/N0 et SNR.

Documenter les conventions de normalisation, le nombre de bits par symbole et les éventuels effets du préfixe cyclique.

Utiliser des simulations Monte-Carlo reproductibles.

Ne pas présenter un BER nul observé comme la preuve d'une probabilité d'erreur nulle.

Afficher le nombre de bits simulés et le nombre d'erreurs observées.

**Validation de phase :** les courbes simulées doivent suivre les résultats théoriques dans les limites statistiques attendues.

---

## PHASE 3 — Fondements mathématiques de l'OFDM

### Expérience 7 : FFT et IFFT

Expliquer :

- La transformée de Fourier discrète.
- La FFT comme algorithme de calcul efficace.
- La transformée inverse IFFT.
- L'orthogonalité des sous-porteuses.
- La représentation fréquentielle et temporelle.

Vérifier numériquement :

FFT(IFFT(X)) ≈ X

Étudier l'espacement entre sous-porteuses.

### Expérience 8 : émetteur OFDM

Implémenter une chaîne :

Bits → Mapping QAM → Allocation des sous-porteuses → IFFT → Préfixe cyclique → Signal OFDM.

Paramètres configurables :

- Nombre de sous-porteuses.
- Nombre de sous-porteuses actives.
- Type de modulation.
- Taille FFT.
- Longueur du préfixe cyclique.
- Nombre de symboles OFDM.
- Espacement des sous-porteuses.

Commencer avec une configuration simple, par exemple une FFT de 64 points.

Prévoir explicitement la gestion des sous-porteuses nulles, de la composante DC et des indices fréquentiels.

### Expérience 9 : OFDM sur canal AWGN

Transmettre des données à travers le canal AWGN.

Implémenter le récepteur idéal :

Signal reçu → Retrait CP → FFT → Extraction des sous-porteuses → Démodulation → Bits récupérés.

Comparer les bits d'origine aux bits récupérés.

**Validation :** le système doit fonctionner sans erreur sur un canal idéal et présenter des performances cohérentes avec les modèles AWGN.

---

## PHASE 4 — Propagation radio et trajets multiples

### Expérience 10 : préfixe cyclique

Expliquer :

- L'interférence entre symboles (ISI).
- La convolution linéaire.
- La convolution circulaire.
- Le rôle du préfixe cyclique.

Comparer les transmissions avec et sans préfixe cyclique.

### Expérience 11 : canal multitrajet

Simuler un canal discret à plusieurs trajets.

Modèle :

y[n] = somme(h[l] × x[n-l]) + w[n]

Étudier :
- Les retards de propagation.
- L'atténuation.
- L'évanouissement sélectif en fréquence.
- La réponse impulsionnelle du canal.
- La réponse fréquentielle.

Commencer avec un canal fixe, puis proposer un canal aléatoire de type Rayleigh.

### Expérience 12 : égalisation

Implémenter :

- Un égaliseur Zero-Forcing (ZF).
- Un égaliseur MMSE.

Comparer :
- Le BER avant et après égalisation.
- La sensibilité aux creux du canal.
- L'amplification du bruit par ZF.

**Validation :** vérifier l'égalisation avec connaissance parfaite du canal avant d'introduire une estimation imparfaite.

---

## PHASE 5 — Synchronisation et estimation de canal

### Expérience 13 : décalage fréquentiel

Simuler un Carrier Frequency Offset (CFO).

Expliquer :
- La perte d'orthogonalité.
- L'interférence entre sous-porteuses (ICI).
- La rotation de phase.
- La dégradation du BER.

Implémenter une première méthode de correction et comparer les performances.

### Expérience 14 : estimation de canal

Ajouter des symboles pilotes.

Implémenter une estimation de canal basée sur les pilotes, puis une interpolation fréquentielle.

Comparer :

- Canal parfaitement connu.
- Canal estimé.
- Canal non corrigé.

Étudier l'erreur quadratique moyenne de l'estimation.

### Expérience 15 : comparaison globale

Faire varier :
- Modulation.
- Eb/N0.
- Nombre de sous-porteuses.
- Longueur CP.
- Canal AWGN ou multitrajet.
- Égaliseur ZF ou MMSE.
- Qualité de l'estimation du canal.

Produire des tableaux et graphiques comparatifs.

---

## PHASE 6 — Application pratique : transmission d'image

### Expérience 16 : transmission d'une image

Créer une expérience permettant de :

1. Charger une petite image locale.
2. Convertir ses octets en bits.
3. Encapsuler les données dans des trames.
4. Moduler les données.
5. Les transmettre par la chaîne OFDM.
6. Simuler les perturbations.
7. Démoduler et reconstruire les bits.
8. Reconstituer l'image reçue.
9. Comparer les résultats.

Utiliser un format de données explicitement documenté.

Prévoir la gestion des tailles, du bourrage, des erreurs de trame et des données corrompues.

Afficher :

- Image originale.
- Image reconstruite.
- BER.
- Nombre d'octets erronés.
- Paramètres de transmission.

Ne pas confondre une corruption d'image avec une représentation fidèle de toutes les erreurs radio : expliquer les limites de cette démonstration.

---

## PHASE 7 — Laboratoire interactif

### Expérience 17 : système complet

Après validation de toutes les phases précédentes, développer une interface Streamlit.

L'utilisateur doit pouvoir :

- Choisir une modulation.
- Régler Eb/N0.
- Sélectionner un modèle de canal.
- Modifier la taille FFT.
- Configurer le préfixe cyclique.
- Activer ou désactiver l'égalisation.
- Choisir une méthode d'estimation de canal.
- Lancer une simulation.
- Visualiser les constellations.
- Observer le spectre du signal.
- Afficher les courbes BER.
- Comparer plusieurs expériences.
- Exporter les graphiques et résultats.

L'interface doit exploiter directement les modules scientifiques existants, sans dupliquer les algorithmes.

Prévoir des paramètres par défaut raisonnables, des validations d'entrées et des messages d'erreur explicites.

# 6. RÈGLES DE RIGUEUR SCIENTIFIQUE

Le laboratoire doit être scientifiquement défendable.

Appliquer les règles suivantes :

1. Définir toutes les variables et leurs unités.
2. Indiquer les hypothèses des modèles.
3. Distinguer bande de base complexe et signal radio réel.
4. Ne pas prétendre simuler une transmission RF physique complète.
5. Justifier la normalisation énergétique.
6. Tenir compte des différences entre Eb/N0, Es/N0 et SNR.
7. Préciser si l'énergie du CP et des pilotes entre dans le bilan énergétique.
8. Documenter les conventions FFT et l'ordre des sous-porteuses.
9. Éviter toute confusion entre puissance, énergie et amplitude.
10. Utiliser des graines aléatoires reproductibles.
11. Indiquer le nombre de bits et d'erreurs pour chaque estimation BER.
12. Fournir des intervalles de confiance lorsque c'est pertinent.
13. Expliquer les limites des approximations.
14. Ne jamais fabriquer de résultats expérimentaux.
15. Ne jamais présenter une courbe illustrative comme un résultat mesuré.

Pour les premières phases, ne pas utiliser de bibliothèques qui implémentent directement toute la chaîne OFDM à notre place. Construire les mécanismes essentiels avec NumPy et SciPy.

# 7. TESTS ET VALIDATION

Créer des tests automatisés couvrant notamment :

- Mapping et démapping des bits.
- Normalisation de l'énergie des symboles.
- Modulation et démodulation sans bruit.
- Inversion FFT/IFFT.
- Construction et suppression du préfixe cyclique.
- Conservation des dimensions.
- Transmission idéale sans erreur.
- Cohérence de la puissance du bruit.
- Reproductibilité des expériences.
- BER théorique et simulé.
- Réponse du canal multitrajet.
- Égalisation avec canal connu.
- Reconstruction des trames binaires.

Utiliser des tolérances numériques appropriées.

Les tests statistiques doivent utiliser des tailles d'échantillon suffisantes et des critères compatibles avec la variabilité Monte-Carlo.

Ne pas utiliser une égalité stricte pour comparer des nombres flottants.

# 8. DOCUMENTATION PÉDAGOGIQUE

Chaque expérience doit avoir son propre document Markdown en français.

Respecter systématiquement cette structure :

## A. Objectif

Expliquer ce que l'expérience cherche à démontrer.

## B. Théorie

Présenter les principes physiques et mathématiques.

## C. Équations

Présenter les équations en LaTeX, définir chaque variable et expliquer leur signification.

## D. Algorithme

Décrire les étapes du traitement du signal.

## E. Implémentation

Expliquer les fonctions Python importantes et les choix techniques.

## F. Exécution

Indiquer la commande exacte permettant de reproduire l'expérience.

## G. Résultats

Présenter les graphiques, les mesures et les observations.

## H. Interprétation

Expliquer pourquoi les résultats obtenus sont cohérents ou non avec la théorie.

## I. Limites

Décrire les hypothèses simplificatrices et les limites de l'expérience.

## J. Questions d'ingénierie

Ajouter trois à cinq questions de compréhension, avec leurs réponses dans une section séparée.

Faire progresser les explications du niveau Licence vers le niveau Master.

Définir les termes techniques avant de les employer dans des démonstrations complexes.

# 9. RAPPORT SCIENTIFIQUE FINAL

Créer un rapport final structuré comme un mémoire technique.

Titre proposé :

**Conception, simulation et analyse des performances d'un système de transmission numérique OFDM sur canaux AWGN et multitrajets**

Structure :

1. Résumé
2. Introduction générale
3. Contexte des communications numériques
4. Principes des modulations numériques
5. Fondements mathématiques de l'OFDM
6. Modélisation des canaux radio
7. Architecture de l'émetteur
8. Architecture du récepteur
9. Méthodologie expérimentale
10. Résultats des simulations
11. Analyse des performances BER
12. Étude de l'égalisation et de l'estimation de canal
13. Application à la transmission d'image
14. Limites du modèle
15. Perspectives : MIMO-OFDM, 5G NR et radio logicielle
16. Conclusion générale
17. Bibliographie
18. Annexes techniques

Citer des références scientifiques fiables et vérifiables.

Ne pas inventer de références bibliographiques, de résultats, de figures ou de mesures.

Le rapport doit être rédigé progressivement à partir des expériences réellement exécutées.

# 10. LIVRABLES FINAUX

Le projet terminé devra comprendre :

- Le code source Python complet.
- Une bibliothèque de simulation réutilisable.
- Les 17 expériences.
- Les tests automatisés.
- Les notebooks pédagogiques.
- Les graphiques scientifiques.
- Les fichiers de résultats CSV.
- Les configurations expérimentales.
- Une interface Streamlit.
- Un guide d'installation.
- Un guide d'utilisation.
- Un glossaire des télécommunications.
- Une documentation mathématique.
- Un rapport scientifique final.
- Un README GitHub professionnel.

Tous les graphiques devront avoir des titres, axes, unités et légendes appropriés.

# 11. MÉTHODE DE TRAVAIL IMPOSÉE

Tu dois suivre le plan dans l'ordre.

Pour chaque phase :

1. Expliquer ce qui va être développé.
2. Présenter les bases théoriques.
3. Implémenter le code.
4. Écrire les tests.
5. Exécuter les tests.
6. Lancer les expériences.
7. Générer les résultats.
8. Interpréter les observations.
9. Mettre à jour la documentation.
10. Produire un bilan de phase.

Ne pas passer silencieusement à la phase suivante lorsqu'un test critique échoue.

Conserver un fichier `PROGRESS.md` indiquant :

- Les phases terminées.
- Les expériences exécutées.
- Les tests réussis ou échoués.
- Les résultats disponibles.
- Les problèmes connus.
- Les prochaines étapes.

Lorsqu'une commande ou une expérience ne peut pas être exécutée dans l'environnement disponible, le signaler clairement au lieu d'inventer son résultat.

Ne pas commencer par l'interface Streamlit.

Ne pas remplacer les implémentations scientifiques par des graphiques fictifs.

# 12. INSTRUCTION DE DÉMARRAGE

Commence maintenant par :

1. Inspecter l'environnement de développement.
2. Créer la structure du projet.
3. Configurer les dépendances et les outils de qualité.
4. Rédiger un README initial.
5. Implémenter la génération binaire.
6. Implémenter la modulation et la démodulation BPSK.
7. Implémenter la modulation et la démodulation QPSK avec mapping Gray.
8. Ajouter les tests correspondants.
9. Créer les premières constellations.
10. Rédiger les explications scientifiques détaillées de ces expériences.

Exécute les tests et les expériences lorsque l'environnement le permet.

Présente ensuite un compte rendu indiquant précisément les fichiers créés, les commandes exécutées, les résultats obtenus et les prochaines étapes.

**Objectif final : disposer d'un laboratoire scientifique OFDM complet, reproductible, pédagogique et techniquement crédible, utilisable comme projet académique avancé et démonstration de compétences en ingénierie des télécommunications.**
