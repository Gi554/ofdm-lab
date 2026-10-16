# Estimation par pilotes : LS et interpolation fréquentielle

## Plan en peigne
Chaque trame OFDM comporte Kp pilotes publics connus, de module 1, et Kd=K-Kp
porteuses de données équiprobables Es=1. Leurs positions sont indexées dans l’ordre
actif -K/2..-1, +1..+K/2. Les extrémités de chaque demi-bande sont des pilotes.
Le pas demandé est un maximum : le dernier intervalle peut être plus court.
Les phases pilotes sont la suite exacte 1, j, -1, -j répétée ; aucune information
utile n’y est encodée. Le plan et les valeurs sont partagés par émetteur/récepteur.

Le mapping, l’IFFT unitaire, le CP et les décisions réutilisent les modules existants.
Aucun bourrage implicite : une trame contient exactement Kd log2(M) bits de données.
Le récepteur écarte les pilotes du BER et de la sortie binaire utile.

## Modèle et estimateur
À timing parfait, CFO nul et CP couvrant la mémoire, Yp=Hp Xp+Wp.
LS donne H_hat_p=Yp/Xp. Comme |Xp|²=1, l’erreur a variance complexe N0.
Une matrice réelle A interpole linéairement les parties réelle et imaginaire de
chaque demi-bande séparément : H_hat_actif=A H_hat_p. Aucune extrapolation et
aucune interpolation à travers DC ; les gardes ne sont pas estimées (valeur 0).

Une estimation est calculée **par trame**, sans accès à H vrai ni lissage temporel.
Pour un canal statique sélectif, elle conserve un biais d’interpolation même sans bruit.
Ce premier estimateur ne connaît ni les retards ni la mémoire du canal ; la simulation
utilise la mémoire uniquement pour vérifier la validité du modèle diagonal.

## MSE analytique sur les porteuses de données
En restreignant A aux données, soit b=A Hp-Hd, C=A Aᵀ et d=Kd.
L’erreur d’estimation est une gaussienne complexe propre de moyenne b, covariance N0 C.
Alors E[MSE]=||b||²/d + N0 tr(C)/d.
Pour la moyenne sur F trames indépendantes :

`Var(MSE_moyenne) = [N0² tr(C²) + 2 N0 b* C b] / (d² F)`.

H vrai intervient ici uniquement pour évaluer l’estimateur. Il n’est pas donné à LS.
Les essais valident les moyennes par Chebyshev et union : rayon sqrt(Var × J/0,01)
pour J essais, couverture simultanée au moins 99 %. Cette borne est conservatrice ;
les références analytiques ne sont pas des courbes empiriques ajustées.

## Énergie et débit
Es_data=Es_pilote=1. L’énergie utile moyenne vaut K. Les pilotes déterministes peuvent
produire un signal CP cohérent ; son énergie ne vaut pas nécessairement Kp C/N.
On calcule exactement x_p=IFFT(grille contenant seulement les pilotes).
Alors E_CP=Kd C/N + somme sur les C derniers échantillons de |x_p|².
Les termes croisés s’annulent en moyenne sur les données indépendantes de moyenne nulle.

La référence **total** utilise Eb=(K+E_CP)/(Kd log2(M)), pilotes et CP inclus.
La référence **data** utilise Eb=1/log2(M), pilotes et CP exclus.
N0=Eb/10^(Eb/N0_dB/10) est référencé à l’émetteur, jamais à l’énergie reçue.
Le débit utile vaut Kd log2(M) Fs/(N+C). Aucune normalisation par réalisation n’est faite.
Plus de pilotes réduit le débit et augmente le coût par bit utile. Les ensembles de
porteuses de données changent aussi avec le pas : une comparaison de densités ne
mesure donc pas uniquement la qualité d’interpolation à ressources identiques.

## Décisions et intervalles
Comparer sans correction, ZF avec H parfait, et ZF avec H_hat. Les creux non inversibles
sont rejetés explicitement, sans epsilon qui masquerait une perte d’information.
Les estimations de différentes données d’une trame partagent du bruit pilote ; leurs
erreurs peuvent être corrélées. Les trames sont indépendantes à H fixé : Clopper-Pearson
par porteuse/bit, puis Bonferroni, fournit un IC conservateur à 95 % par ligne.
Aucune couverture globale de l’ensemble des courbes BER n’est revendiquée.
Ne pas réutiliser ces IC après une moyenne temporelle de H_hat sans nouvelle analyse.

## Limites et référence
Canal fixe ou une réalisation Rayleigh statique ; pas de moyenne d’ensemble Rayleigh,
CFO, Doppler ni synchronisation imparfaite dans cette expérience. L’égaliseur ZF
avec H_hat n’est pas un détecteur optimal tenant compte de l’incertitude du canal.

van de Beek, Edfors, Sandell, Wilson et Börjesson, « On channel estimation in OFDM
systems », VTC 1995, pages 815–819, DOI 10.1109/VETEC.1995.504981,
[notice institutionnelle](https://ltu.diva-portal.org/smash/record.jsf?pid=diva2%3A1001468).
Cette référence situe LS et MMSE ; le présent lot implémente uniquement LS et une
interpolation linéaire explicite, sans revendiquer leurs résultats MMSE.
