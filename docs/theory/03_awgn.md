# Bruit AWGN et rapports énergétiques

## Modèle discret en bande de base complexe

Le canal ajoute un bruit : $y_i=s_i+n_i$. Les symboles s_i sont des amplitudes complexes
normalisées, y_i leurs observations. Le bruit est $n_i=n_{I,i}+j n_{Q,i}$, avec deux
composantes indépendantes gaussiennes de moyenne nulle et de variance N0/2.
Ainsi E|n_i|²=N0 et E[n_i²]=0 (circularité). Des échantillons indépendants donnent une
corrélation $E[n_i n_j^*]=N_0\delta_{ij}$ : le bruit est blanc dans ce modèle discret.
Sa densité complexe est $p(n)=\exp(-|n|^2/N_0)/(\pi N_0)$.

La normalité et l’indépendance sont imposées par le générateur. Les tests de moments,
corrélation et pseudo-covariance vérifient des conséquences ; ils ne prouvent pas à eux
seuls toutes les propriétés d’un processus gaussien. Une gaussienne a un support infini.
Ce modèle idéalise le bruit thermique et exclut interférences et perturbations impulsives.

## Énergie, puissance et amplitude

À l’instant de décision d’un symbole, Es est l’énergie moyenne de l’alphabet et k le
nombre de bits par symbole. Sans codage ni surcoût, Eb=Es/k. Toutes les énergies sont
normalisées ici ; aucune fréquence d’échantillonnage ni calibration en watts n’est fixée.
N0 est ici le paramètre de variance du modèle discret, pas une mesure physique en W/Hz.

$$\gamma_b=10^{(E_b/N_0)_{dB}/10},\quad N_0=\frac{E_s}{k\gamma_b},\quad
(E_s/N_0)_{dB}=(E_b/N_0)_{dB}+10\log_{10}k.$$

Les dB de rapports d’énergie/puissance utilisent 10 log10, pas 20 log10.
La dispersion (écart-type) sur chaque axe est sqrt(N0/2), et non N0.
Le bruit est calibré avec Es de l’alphabet, jamais avec la puissance mesurée du tirage
ou du signal reçu. Un tirage QAM fini a une moyenne énergétique qui fluctue.

## SNR échantillonné et surcoûts

Avec L échantillons par symbole, une mise en forme discrète conservant
$\sum_n|x[n]|^2=E_s$ par symbole donne une puissance moyenne Es/L.
Si chaque échantillon bruité a E|n[n]|²=N0, alors
$SNR_{dB}=(E_s/N_0)_{dB}-10\log_{10}L$.
Les expériences actuelles ont L=1, donc SNR=Es/N0 ; le SNR mesuré fluctue.
Cette convention ne modélise pas toute chaîne de filtrage suréchantillonnée.
Elle ne doit pas être appliquée automatiquement à l’OFDM : il faudra préciser l’énergie
des pilotes et du CP, les porteuses nulles et la normalisation FFT. Aucun de ces surcoûts
n’entre encore dans le bilan de phase 2.

## Référence
David Tse et Pramod Viswanath, *Fundamentals of Wireless Communication*, Cambridge
University Press, 2005, [appendice A](https://web.stanford.edu/~dntse/Chapters_PDF/Fundamentals_Wireless_Communication_AppendixA.pdf),
sections A.1 et A.2. Référence officielle des auteurs, vérifiée le 16 octobre 2026.
