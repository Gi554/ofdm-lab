# Convolution multitrajet et préfixe cyclique

Le modèle causal discret est $y[n]=\sum_{l=0}^{L-1}h[l]x[n-l]+w[n]$.
x et y sont des amplitudes de bande de base normalisées ; h est un gain complexe sans
unité, n et l des indices d’échantillons. Le délai physique est l/Fs secondes.
La convolution est appliquée au flux entier, avec état initial nul et queue complète.
La longueur est Nx+L−1 ; le récepteur n’utilise explicitement que les Nx échantillons du burst attendu.
La mémoire D est le dernier retard non nul ; les zéros terminaux n’augmentent pas D.

Si le CP de C échantillons vérifie C>=D, le retrait du CP transforme chaque fenêtre utile
en convolution circulaire. Avec la FFT unitaire des signaux :

$$Y[k]=H[k]X[k]+W[k],\quad H[k]=\sum_l h[l]e^{-j2\pi kl/N}.$$

H se calcule donc par FFT **non normalisée** de h, même si X et Y utilisent la FFT unitaire.
Le bruit reste de variance N0 par case. Un CP insuffisant laisse une interférence entre
symboles et entre sous-porteuses ; un égaliseur diagonal ne peut pas l’annuler exactement.
Le CP ne remplace pas l’égalisation des gains complexes H[k].

## Canaux étudiés

Le canal fixe a deux trajets aux retards 0 et 6, de gains 1 et −0,95, puis une normalisation
déterministe à somme|h|²=1, explicitement configurée. La normalisation n’est pas imposée
par la fonction de convolution. Les sous-porteuses peuvent subir de profonds creux.
Le canal Rayleigh tire des gains indépendants h[d_l]~CN(0,p_l/somme p).
La somme des puissances **attendues** vaut 1. La somme d’énergie d’une réalisation fluctue
et n’est jamais forcée à 1. Une réalisation est statique pendant le burst, sans Doppler.
Le profil utilise les retards 0,2,6 et les puissances 0,6/0,3/0,1.

Le modèle n’est pas un ray-tracing physique et n’inclut pas d’étalement Doppler, de retards
fractionnaires ou de path loss dépendant d’une distance. Les retards sont des entiers.
Référence vérifiée : Tse et Viswanath, *Fundamentals of Wireless Communication*, Cambridge,
2005, [chapitre 3, diversité fréquentielle et OFDM](https://web.stanford.edu/~dntse/Chapters_PDF/Fundamentals_Wireless_Communication_chapter3.pdf),
consulté le 16 octobre 2026. Les conventions de normalisation sont dérivées ci-dessus.
