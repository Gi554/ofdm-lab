# Méthodologie

Procéder dans l’ordre du cahier des charges. Pour chaque phase : expliciter les hypothèses,
implémenter, tester, exécuter les expériences, mesurer puis interpréter et documenter.
Un échec critique bloque la progression. L’interface ne commencera qu’après validation du moteur.

Une constellation est un alphabet de symboles complexes. Son énergie est la moyenne de
|s|² sur les points équiprobables. Elle est ici sans dimension et normalisée à 1.
Les bits sont indépendants et équiprobables dans le modèle du générateur.
Le débit binaire Rb (bit/s) et le débit symbole Rs (symbole/s) vérifient Rb=k Rs,
mais aucune durée physique n’est choisie dans ces trois expériences.

Le BER observé est le nombre d’erreurs divisé par le nombre de bits comparés.
Sur canal idéal déterministe, une restitution exacte valide l’inversion du mapping.
Elle n’établit aucune performance sous bruit. En Monte-Carlo futur, enregistrer le nombre
d’erreurs et fournir des intervalles binomiaux. Zéro erreur sur N essais indépendants
ne démontre pas une probabilité nulle : borne supérieure unilatérale 95 %,
1−0,05^(1/N), approximativement 3/N. Cette borne ne représente pas un modèle du canal idéal.

Les figures utilisent des index sans unité et des amplitudes normalisées ; aucune
courbe illustrative n’est présentée comme une mesure RF. Les sorties JSON enregistrent
la graine et la version NumPy. Les dépendances résolues sont archivées après installation.
