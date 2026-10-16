# Modulations QAM carrées avec étiquetage Gray

La modulation d’amplitude en quadrature (QAM) combine deux alphabets réels indépendants,
portés par I et Q. Pour M=L² points, L niveaux par axe portent chacun p=log₂(L) bits.
Le symbole transporte k=2p=log₂(M) bits : 4 en 16-QAM, 6 en 64-QAM.

## Mapping explicite

Les k bits sont regroupés en p bits I puis p bits Q, poids fort en tête.
Le mot de chaque axe est interprété comme un entier Gray g. Son indice binaire est
$r=g\oplus(g\gg1)\oplus(g\gg2)\oplus\cdots$, où ⊕ désigne le XOR et ≫ le décalage.
La coordonnée non normalisée est a=L−1−2r. En 16-QAM :
00 → +3, 01 → +1, 11 → −1, 10 → −3. Aucune norme radio particulière n’est revendiquée.

## Énergie et distance minimale

L’alphabet d’un axe est {−(L−1), …, −1, +1, …, +(L−1)} et sa moyenne quadratique
équiprobable vaut (L²−1)/3. Les deux axes donnent une énergie brute 2(M−1)/3.

$$s=\frac{a_I+ja_Q}{\sqrt{2(M-1)/3}},\qquad E_s=1,\qquad E_b=1/\log_2 M.$$

Les amplitudes et énergies sont normalisées, sans unité physique fixée.
La distance minimale vaut $d_{min}=\sqrt{6/(M-1)}$ : les points se rapprochent quand
M augmente à Es constant. L’énergie d’un symbole individuel QAM n’est pas constante ;
Es=1 est une propriété de l’alphabet équiprobable, pas de toute séquence finie.

## Détection cohérente

Le récepteur décide indépendamment sur I et Q avec des seuils à mi-distance des niveaux.
Une égalité exacte choisit la coordonnée supérieure, donc la région positive au seuil nul.
Le récepteur retrouve g=r⊕(r≫1), puis restitue les bits I suivis des bits Q.
La saturation aux niveaux extrêmes réalise la décision du plus proche point de l’alphabet.
Cette décision est optimale au sens distance euclidienne en AWGN circulaire équiprobable.

## Débit et limites

Sans codage ni surcoût, Rb=k Rs : à débit symbole Rs fixé, davantage de bits sont transmis
avec la 64-QAM. Cela ne fixe pas une efficacité en bit/s/Hz sans préciser la mise en forme
et la bande occupée. Le rapprochement des points rend les décisions plus sensibles aux
perturbations à Es fixé. Les performances BER à Eb/N0 fixé seront mesurées en phase 2 ;
aucune performance bruitée n’est déduite des essais idéaux.
