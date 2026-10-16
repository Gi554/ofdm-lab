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
Ne pas mélanger refonte de style et changement scientifique. Ne pas réécrire l’historique publié.

## Branches, pull requests et fusions

`main` est la version validée et la branche par défaut. `staging` est la branche d’intégration.
Le cycle normal de chaque fonctionnalité est :

1. Mettre à jour les références distantes et créer `codex/<fonctionnalite>` depuis `origin/staging`.
2. Implémenter, tester, documenter, puis faire les commits et pousser la branche.
3. Ouvrir une PR vers `staging`, attendre tous les contrôles et fusionner avec un **merge commit**.
4. Ouvrir une PR de `staging` vers `main`, attendre tous les contrôles et fusionner avec un **merge commit**.

Le propriétaire a autorisé ce cycle complet pour chaque fonctionnalité. Aucune confirmation
supplémentaire de routine n’est nécessaire. Les échecs et les conflits doivent être corrigés
avant fusion. Ne pas contourner les protections, pousser directement sur les branches
permanentes, utiliser squash/rebase pour une fusion, ni supprimer `main` ou `staging`.
Les merge commits conservent l’historique détaillé des fonctionnalités.

La CI refuse une PR vers `main` dont la branche source n’est pas `staging`.
Les deux branches permanentes exigent les contrôles CI et une PR avant fusion.
Les règles persistantes pour les prochains travaux sont dans [AGENTS.md](AGENTS.md).

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
