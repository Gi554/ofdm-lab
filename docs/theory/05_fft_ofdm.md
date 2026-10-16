# FFT, orthogonalité et conventions OFDM

La DFT représente une séquence par une combinaison d’exponentielles complexes.
La FFT est un algorithme efficace pour la calculer ; elle n’est pas une autre transformée.
Le laboratoire utilise NumPy avec `norm="ortho"`, sur le dernier axe :

$$X[k]=\frac{1}{\sqrt N}\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N},\qquad
x[n]=\frac{1}{\sqrt N}\sum_{k=0}^{N-1}X[k]e^{j2\pi kn/N}.$$

N est le nombre d’échantillons utiles et de cases fréquentielles, k et n des indices sans unité.
Les colonnes $B_{nk}=e^{j2\pi nk/N}/\sqrt N$ vérifient BᴴB=I : elles sont orthonormales.
Parseval donne somme|x|²=somme|X|². La transformation ne change donc pas l’énergie.

L’ordre natif est DC, fréquences positives, puis négatives. Pour N pair, la case N/2
représente −Fs/2. `fftshift` sert aux figures, jamais à l’allocation native.
À espacement Δf [Hz], Fs=N Δf [échantillons/s] et Tu=1/Δf [s].
Cette orthogonalité porte sur une fenêtre utile synchronisée de durée Tu.
Aucune symétrie hermitienne n’est imposée : le signal est une bande de base complexe.

Référence vérifiée : [NumPy, DFT et normalisation](https://numpy.org/doc/stable/reference/routines.fft.html),
consultée le 16 octobre 2026. Les tests comparent aussi à la définition matricielle indépendante.

## Allocation et chaîne OFDM

La configuration impose N pair, K pair <=N−2 et 0<=C<=N, où C est la longueur CP.
Les bits sont mappés dans l’ordre fréquentiel signé −K/2,…,−1,+1,…,+K/2.
Les indices natifs sont ces entiers modulo N ; DC (0), Nyquist (N/2) et les gardes
restent nuls. Il n’y a pas de pilotes dans cette phase. Le CP copie les C derniers
échantillons utiles au début du symbole ; pour C=0, aucune copie n’est ajoutée.
Le récepteur connaît le début du premier CP et la configuration, retire C échantillons,
applique la FFT unitaire puis extrait les K cases dans le même ordre que l’émetteur.
Les blocs incomplets sont refusés ; aucun bourrage ou en-tête caché n’est utilisé.

## Bilan énergétique : deux références explicites

Pour Es=1 sur chaque alphabet de données et k bits par symbole QAM :

$$E_u=K,\quad E_{CP}=KC/N,\quad E_t=K(1+C/N),\quad P=K/N.$$

Ce sont des moyennes d’ensemble en unités normalisées ; le CP d’un tirage donné
ne porte pas nécessairement exactement C/N fois l’énergie utile. La FFT unitaire
préserve la variance N0 du bruit blanc sur chaque case active ; les cases nulles
ne justifient pas de multiplier cette variance par N/K.

- Référence `useful` : Eb=1/k, N0=1/(k γb). Le CP n’altère pas le BER sur AWGN.
- Référence `total` : Eb=(1+C/N)/k, N0=(1+C/N)/(k γb). Le détecteur dispose d’un
  Eb/N0 utile plus faible de 10 log10(1+C/N) dB à rapport déclaré identique.

Le SNR par échantillon attendu est 10 log10((K/N)/N0). Les pilotes et le codage
ne sont pas inclus. Il ne faut pas renormaliser chaque trame selon son énergie mesurée.
Le débit utile sans codage est K k Fs/(N+C) bit/s. À N=64,K=52,C=16,k=2 et Δf=15 kHz,
il vaut 1 248 000 bit/s. Ces énergies discrètes n’ont pas de calibration en joules.

Le CP n’apporte ici aucun gain contre l’AWGN. Son rôle contre la convolution multitrajet
sera démontré en phase 4 ; aucun résultat de cette phase n’en revendique déjà la validation.
