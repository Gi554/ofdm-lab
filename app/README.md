# Laboratoire interactif OFDM

Depuis la racine du dépôt, avec Python 3.11 ou ultérieur :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,app]"
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py --server.address 127.0.0.1
```

Ouvrir l’URL locale affichée (habituellement http://127.0.0.1:8501). Arrêter avec Ctrl+C
pour libérer le port. Après modification du code, redémarrer le serveur (surveillance
automatique des fichiers désactivée pour une exécution stable). Aucun compte ni hébergement externe n’est requis. Ne pas lancer
avec `python app/streamlit_app.py` : le contexte de session Streamlit est nécessaire.

## Utilisation

- **Simulation** : un calcul initial est affiché. Régler les paramètres dans la barre
  latérale, puis cliquer sur Lancer la simulation. Les anciennes mesures ne sont jamais
  réétiquetées avec des réglages non exécutés. Constellations, DSP Welch et canal sont
  consultables dans les onglets ; CSV, JSON et PNG sont téléchargeables.
- **Comparaisons** : choisir jusqu’à sept points Eb/N0 puis lancer le balayage. Les cinq
  modes sont appariés à chaque point ; le canal reste fixé et les graines sont exportées.
  Jusqu’à huit expériences de simulation peuvent être conservées dans la session.
- **Image** : mire incluse ou PNG chargé, au maximum 128×128 pixels et 2 Mio. Les images
  restent en mémoire et ne sont pas écrites dans le dépôt. Cliquer sur Transmettre l’image.
  Original, diagnostic et blocs acceptés sont distincts ; magenta indique les effacements.
  La taille de l’image détermine son nombre de trames, indépendamment du curseur des
  essais binaires. Maximum 4 096 trames image pour le calcul interactif.
- **Repères** : définitions, normalisations, intervalles et limites scientifiques.

## Périmètre

FFT32/64/128/256, au moins huit porteuses actives, CP0..N, quatre modulations,
AWGN/multitrajets/Rayleigh statique, ZF/MMSE et H connu/LS interpolé/sans correction.
Les essais binaires sont limités à 512 trames par point, avec Fs960kHz et CFO nul,
timing parfait. Les expériences CFO restent disponibles séparément.
Le spectre est une DSP estimée sur au plus 8 192 échantillons ; les constellations
montrent au plus 2 048 symboles de données. Les compteurs portent sur le calcul complet.

Les IC BER sont conditionnels à H et à 95 % par ligne. CP insuffisant : résultats
uniquement descriptifs. L’image déterministe utilise Eb/N0 nominal d’alphabet et publie
son énergie réelle ; ses BER n’ont pas d’IC binomial. Les modes MMSE compensent le gain
pour décider, mais les constellations montrent les estimations avant cette compensation.

Cette livraison est une application locale. Aucun hébergement public n’est configuré.
Les paramètres ne sont pas enregistrés durablement : exporter avant de fermer la session.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe experiments/17_interactive_lab.py
```

Les scénarios Streamlit AppTest nécessitent l’extra app et des sockets locales autorisées.
Sans Streamlit, le fichier de tests d’interface est ignoré ; la CI installe dev et app et
exécute toute la suite. AppTest vérifie calcul, état conservé, migration d’un ancien
balayage, historique, image, MMSE/pilotes et avertissement de CP court.
Le contrôle navigateur complète ces tests ; il ne constitue pas une mesure de charge
multiutilisateur ou une garantie de compatibilité avec tous les navigateurs.
