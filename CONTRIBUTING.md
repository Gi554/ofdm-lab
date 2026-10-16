# Contribuer à OFDM Lab

## Développement

Installer le projet avec `python -m pip install -e ".[dev]"` dans un environnement virtuel.
Avant chaque commit :

```shell
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

## Commits par fonctionnalité

Chaque fonctionnalité forme un commit cohérent : code, tests et explications associées.
Utiliser un sujet explicite : `feat(bits): ...`, `feat(modulation): ...`,
`fix(channel): ...`, `test(ofdm): ...` ou `docs(experiments): ...`.
Ne pas mélanger refonte de style et changement scientifique. Les fonctionnalités suivantes
se développent sur une branche `codex/<fonctionnalite>` et se proposent par pull request.
Ne pas réécrire l’historique publié sans demande explicite.

## Rigueur scientifique

Documenter les hypothèses, normalisations, graines, unités et limites.
Enregistrer les effectifs et erreurs mesurées. Réexécuter les expériences touchées.
Un résultat simulé ne doit jamais être remplacé par une illustration fictive.
La validation scientifique précède le développement de l’interface.

## Fichiers publiés

Ne pas versionner environnements virtuels, secrets, chemins personnels, caches ou dossiers
locaux d’assistants. Les petites données scientifiques reproductibles sont conservées
avec leurs paramètres et leur version NumPy. Les sorties volumineuses seront publiées
séparément avec une méthode de reproduction.
