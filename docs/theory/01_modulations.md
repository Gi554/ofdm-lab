# Bits, symboles et modulations cohérentes

Une modulation transforme des groupes de k bits en un point complexe s=I+jQ.
L’alphabet contient M=2^k points. La représentation I/Q décrit une enveloppe de bande
 de base ; elle ne constitue pas à elle seule une simulation d’une chaîne RF.

Pour un alphabet équiprobable :
$$E_s=\frac{1}{M}\sum_{m=0}^{M-1}|s_m|^2,\qquad E_b=E_s/k.$$
I et Q sont des amplitudes normalisées ; Es et Eb sont des énergies normalisées.
Avec des impulsions de durée et d’énergie physique définies, leur conversion en joules
demanderait une convention supplémentaire.

En BPSK, $s=1-2b$ et $\hat b=\mathbf{1}_{\Re(y)<0}$.
Le seuil est le milieu des deux points, donc la décision du plus proche voisin.
En QPSK,
$$s=\frac{(1-2b_I)+j(1-2b_Q)}{\sqrt{2}}.$$
Les quatre points ont tous |s|²=1, et les deux décisions sont indépendantes.
L’ordre circulaire 00, 01, 11, 10 est Gray : chaque voisin diffère d’un seul bit.
Deux bits sont portés car quatre choix distincts donnent log₂(4)=2.
La distance minimale QPSK vaut √2 contre 2 en BPSK à Es identique.
Cela ne permet pas de conclure sur leur BER à Eb identique sans un modèle de bruit.

Sous AWGN cohérent, sans codage, la future référence est
$P_b=Q(\sqrt{2E_b/N_0})$, où
$Q(x)=\frac{1}{\sqrt{2\pi}}\int_x^\infty e^{-t^2/2}\,dt$.
Ce résultat n’est pas encore testé ici. Pour le bruit complexe : E|n|²=N0,
chaque composante réelle a variance N0/2 ; Es/N0=k Eb/N0.
Le SNR échantillonné OFDM dépendra aussi des porteuses actives et des surcoûts CP/pilotes.
