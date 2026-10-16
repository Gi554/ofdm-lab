# Reproduire les validations et expériences

Depuis la racine du dépôt, après création d’un venv et installation selon le README :

```shell
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python experiments/01_binary_generation.py
python experiments/02_bpsk.py
python experiments/03_qpsk.py
```

Utiliser le Python du venv : `.venv/Scripts/python.exe` sous Windows ou
`.venv/bin/python` sous Linux/macOS. Les sorties des expériences sont écrasées lors
de chaque exécution. Le bilan réellement obtenu est consigné dans PROGRESS.md.
Les fichiers requirements-lock.txt et configs/fundamentals.json décrivent l’environnement
résolu et les paramètres scientifiques des premières expériences.
