# CFO : fréquence, projection FFT et correction

On modélise un défaut constant de l’oscillateur du récepteur après le canal :

`r[n] = y[n] exp(j 2π ε n/N) + w[n]`, avec `ε = Δf / Δf_porteuses`.

Le temps est en échantillons, Δf en Hz. Le flux inclut le CP et la phase ne repart
pas de zéro à chaque symbole. À N=64 et Δf_porteuses=15 kHz, ε=0,15 vaut 2 250 Hz.
Le module du signal et son énergie sont conservés. Le bruit complexe circulaire
est ajouté après la rotation ; sa loi est invariante par une correction unitaire.

## Projection et ICI

Pour une porteuse isolée, la fraction complexe projetée sur la case décalée de q vaut
`C[q] = (1/N) sum(n=0..N-1) exp(j 2π (ε-q)n/N)`.
La somme des N puissances vaut 1 ; la puissance sur la case initiale est |C[0]|².
La fuite totale vaut 1-|C[0]|², y compris vers les gardes. Cette fuite de porteuse
isolée n’est pas le rapport ICI/signal d’un OFDM chargé avec canal sélectif.
Un CFO entier décale les cases : il ne produit pas la dispersion d’un CFO fractionnaire.

La multiplication commune par une phase conserve les produits scalaires entre signaux
émis. La « perte d’orthogonalité » désigne ici leur désalignement avec la base FFT du
récepteur : F D F* devient non diagonale, même si cette matrice reste unitaire.
Pour la fenêtre utile débutant à n_m, le coefficient diagonal contient aussi
`exp(j 2π ε n_m/N)` : la rotation commune s’accumule de symbole en symbole.

## Estimation CP à début connu

Le CP répète la fin utile avec N échantillons d’écart. Pour un FIR de mémoire d,
seules les paires du CP à partir de d sont débarrassées du symbole précédent.
On utilise `R = sum conj(r[m(N+C)+p]) r[m(N+C)+p+N]`, p=d..C-1.
Alors `ε_hat = angle(R)/(2π)`. L’implémentation met les deux signaux à une même
échelle avant la corrélation pour éviter les dépassements ; le champ correlation
contient cette corrélation mise à l’échelle. La cohérence normalisée est un diagnostic,
pas un intervalle de confiance ni une probabilité de réussite.

Le CP doit satisfaire **C>d**, plus strict que C≥d pour l’égalisation. La méthode
suppose le début du burst et une borne correcte de mémoire connus. Elle estime un CFO
constant, modulo 1 ; les bornes ±0,5 sont ambiguës. Par exemple ε=0,7 devient -0,3.
Aucune estimation du décalage entier ni du début de trame n’est encore implémentée.

## Correction et limites

La correction multiplie tout le flux par `exp(-j 2π ε_hat n/N)` avec la même origine.
Une estimation oracle utilise ε réel et sert uniquement de témoin scientifique.
Le résidu ε-ε_hat continue de tourner sur les longs bursts ; une faible RMSE de
fréquence ne garantit donc pas un BER faible. Un suivi de phase ou une réestimation
par blocs serait une extension, pas une propriété de ce premier estimateur.

Les BER sont descriptifs : l’estimation commune et la rotation non stationnaire
empêchent d’appliquer directement un IC binomial à tous les bits. Les statistiques
RMSE utilisent des bursts indépendants ; aucun IC RMSE n’est revendiqué.
La connaissance de H reste parfaite dans l’égaliseur ZF pour isoler le CFO.

## Référence primaire

van de Beek, Sandell et Börjesson, « ML estimation of time and frequency offset in
OFDM systems », IEEE Transactions on Signal Processing 45(7), 1800–1805, 1997,
[notice institutionnelle et DOI](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2%3A989074).
La corrélation CP étudiée ici utilise un timing connu ; elle ne constitue pas une
implémentation complète de leur recherche conjointe du temps et de la fréquence.
