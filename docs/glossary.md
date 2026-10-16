# Glossaire

- **Bit** : chiffre binaire, 0 ou 1.
- **Symbole** : point de l’alphabet transmis, portant k bits.
- **I/Q** : composantes réelle (en phase) et imaginaire (quadrature).
- **Bande de base complexe** : représentation du signal avant transposition RF.
- **BPSK** : modulation de phase à deux états opposés, k=1.
- **QPSK** : modulation de phase à quatre états, k=2.
- **Gray** : étiquetage dont deux voisins géométriques diffèrent d’un bit.
- **Es / Eb** : énergie par symbole / par bit, Es=k Eb hors surcoûts.
- **BER / SER** : proportion d’erreurs binaires / de symboles.
- **AWGN** : bruit additif blanc gaussien (phase suivante).
- **OFDM** : multiplexage de sous-porteuses orthogonales (phase 3).
- **CP** : préfixe cyclique, copie de la fin du symbole OFDM.

- **QAM** : modulation d’amplitude en quadrature, combinant plusieurs niveaux I et Q.
- **Distance minimale** : plus petite distance euclidienne entre deux points de constellation.

- **N0 discret** : variance complexe totale du bruit dans la convention du laboratoire.
- **Circularité** : invariance de la loi du bruit complexe par rotation de phase.
- **SNR** : rapport puissance moyenne du signal sur puissance moyenne du bruit.

- **Intervalle de confiance (IC)** : procédure dont la couverture répétée du paramètre est au moins le niveau annoncé, sous les hypothèses.
- **Clopper–Pearson** : intervalle binomial exact, généralement conservateur.
- **Bonferroni** : répartition du risque global entre plusieurs bornes pour garantir leur couverture simultanée.
- **Hamming** : nombre de positions binaires différentes entre deux mots.

- **DC** : case fréquentielle de fréquence nulle, laissée vide ici.
- **FFT/IFFT unitaires** : DFT directe/inverse normalisées par 1/sqrt(N), conservant l’énergie.
- **Porteuse de garde** : case fréquentielle laissée nulle au bord du bloc.
- **DSP** : densité spectrale de puissance ; estimation discrète en amplitude normalisée²/Hz.

- **ISI** : interférence entre symboles successifs due à une mémoire de canal non couverte.
- **ZF** : Zero-Forcing, inversion du gain connu H, avec amplification du bruit dans les creux.
- **MMSE** : estimation linéaire minimisant l’erreur quadratique moyenne, généralement biaisée.
- **PDP** : profil de puissances moyennes des trajets (Power Delay Profile).
- **Rayleigh statique** : gains complexes gaussiens tirés une fois et fixes pendant le burst.

- **CFO** : différence de fréquence d’oscillateurs, normalisée ici par l’espacement entre porteuses.
- **ICI** : interférence entre sous-porteuses dans la projection FFT du récepteur.
- **Oracle** : témoin utilisant une grandeur réelle connue uniquement par la simulation.

- **Pilote** : symbole émis public permettant d’estimer le canal, sans bit utile.
- **LS** : moindres carrés ; ici H estimé aux pilotes par Yp/Xp.
- **Biais d’interpolation** : différence persistante entre le canal réel et son approximation interpolée, même sans bruit.

- **CRC32** : contrôle de détection d’erreurs ; ne corrige pas et n’authentifie pas les données.
- **Effacement** : bloc dont les données fiables manquent, signalé par masque et magenta dans les vues image.
- **RGB8** : trois composantes rouge/vert/bleu de huit bits par pixel.
