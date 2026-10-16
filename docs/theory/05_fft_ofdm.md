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
