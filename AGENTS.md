# Instructions persistantes — OFDM Lab

## Préférences explicites du propriétaire

Ces règles ont été demandées le 16 octobre 2026 et s’appliquent aux travaux suivants.
Le dépôt GitHub est public : https://github.com/Gi554/ofdm-lab.

## Processus Git obligatoire

- `main` contient les versions validées ; `staging` sert à l’intégration.
- Démarrer chaque fonctionnalité sur une branche `codex/<fonctionnalite>` depuis `origin/staging` à jour.
- Faire des commits cohérents par fonctionnalité, avec tests et documentation associés.
- Pousser la branche et ouvrir une PR vers `staging` ; attendre la réussite de tous les contrôles.
- Fusionner la PR avec un **merge commit** pour conserver les commits de chaque fonctionnalité.
- Ouvrir ensuite une PR `staging` → `main`, vérifier ses contrôles puis la fusionner avec un merge commit.
- Le propriétaire autorise ce cycle commit → PR → validation → merge pour chaque fonctionnalité.
  Procéder sans redemander une confirmation de routine, dans le périmètre du travail demandé.
- Ne jamais fusionner avec des contrôles échoués ou en attente, ni contourner les protections.
- Ne pas pousser directement sur `staging` ou `main`, forcer une poussée, ou réécrire l’historique publié.
- `main` reste la branche par défaut. Ne jamais supprimer `main` ou `staging`.
- Conserver les PR et leur contexte de validation. Référencer les liens dans le compte rendu.

## Validation scientifique

Suivre le cahier des charges par phases. Valider le moteur avant toute interface.
Documenter hypothèses, unités, normalisations, graines, effectifs, erreurs et limites.
Ne jamais inventer de résultats. Exécuter les tests et les expériences affectés.
Maintenir `PROGRESS.md` à jour ; documenter en français.
La CI exécute Pytest, Ruff et les expériences sur Python 3.11, 3.12 et 3.13.

## Publication propre

Aucun dossier OpenAI/Codex local, environnement virtuel, cache, secret ou chemin personnel
ne doit être publié. Respecter `.gitignore`. `AGENTS.md` est le fichier de mémoire projet
versionné ; les éventuels journaux de machine restent dans `.local/`, ignoré par Git.
