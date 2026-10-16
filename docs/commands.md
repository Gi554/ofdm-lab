# Reproduire les validations et expériences

Depuis la racine du dépôt, après création d’un venv et installation selon le README :

```shell
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python experiments/01_binary_generation.py
python experiments/02_bpsk.py
python experiments/03_qpsk.py
python experiments/04_qam.py
python experiments/05_awgn.py
python experiments/06_ber_comparison.py
python experiments/07_fft_ifft.py
python experiments/08_ofdm_transmitter.py
python experiments/09_ofdm_awgn.py
python experiments/10_cyclic_prefix.py
python experiments/11_multipath_channel.py
python experiments/12_channel_equalization.py
```

Utiliser le Python du venv : `.venv/Scripts/python.exe` sous Windows ou
`.venv/bin/python` sous Linux/macOS. Les sorties des expériences sont écrasées lors
de chaque exécution. Le bilan réellement obtenu est consigné dans PROGRESS.md.
Les fichiers requirements-lock.txt et configs/fundamentals.json décrivent l’environnement
résolu et les paramètres scientifiques des premières expériences.
