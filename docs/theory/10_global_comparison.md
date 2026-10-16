# Comparaisons globales : ressources, énergie et limites

## Protocole apparié
Chaque essai fixe modulation, Eb total/N0, taille FFT, CP, canal et pas pilote.
Les cinq modes reçoivent les mêmes données, pilotes et bruit : sans correction,
ZF/MMSE à H parfait, puis ZF/MMSE à H estimé LS interpolé par trame.
Le témoin parfait conserve les pilotes : il ne bénéficie pas d’un débit artificiellement
supérieur. Le BER ne compte que les données. Les symboles pilotes, le CP et les
gardes sont exclus du nombre de bits utiles, mais pilotes et CP entrent dans Eb total.
Le bilan exact du CP pilote déterministe est celui de l’expérience 14.

Les essais de configurations différentes utilisent des graines indépendantes dérivées
d’une graine racine. L’appariement concerne les cinq modes d’un essai ; pas deux points
de modulations ou densités différentes. Aucun classement universel n’est déduit.

## FFT et canal physique
Fs=960 kHz et K/N=13/16 sont fixes : N=64/K=52 ou N=128/K=104.
L’espacement vaut 15 kHz ou 7,5 kHz ; la bande active va dans les deux cas de
-390 kHz à +390 kHz, DC exclue. La durée utile double quand N double.
Les retards FIR restent en échantillons à Fs constant, donc en secondes inchangées.
CP=0 ou 16 échantillons (0 ou 16,667 microsecondes). Le CP couvre la mémoire 6
lorsqu’il vaut 16, mais sa proportion et son coût changent avec N.

Un pas pilote donné correspond à une distance en Hz plus faible à N=128. Le nombre
de pilotes, les données observées, le débit et le coût énergétique changent aussi.
Ces variations couplées interdisent d’attribuer tout écart à la seule taille FFT.
La normalisation des canaux et la réalisation Rayleigh sont conservées de la phase 4.

## ZF et MMSE avec H estimé
Les poids sont 1/H_model et H_model*/(|H_model|²+N0). La décision MMSE compense
le gain calculé avec ce même H_model. Pour un H_model non nul, cette compensation
retrouve Y/H_model, donc les mêmes décisions scalaires que ZF, même si le modèle
est estimé ou si le CP est court. Ce fait algébrique n’établit pas que ces décisions
sont optimales face à l’incertitude du canal ou à l’ISI.

La MSE des estimations de symboles est mesurée avant cette compensation de décision.
Elle peut différer entre ZF et MMSE. Avec canal connu et modèle diagonal valide,
MMSE minimise la MSE linéaire ; avec H estimé ou ISI, cette optimalité n’est pas
revendiquée. On mesure séparément la MSE de H estimé sur les porteuses de données.

## Références BER et intervalles
À CP suffisant et canal parfaitement connu, chaque porteuse de données voit un
Eb utile/N0 effectif |H[k]|²/(log2(M) N0). La référence est la moyenne des BER exacts
AWGN de ces porteuses, conditionnelle à H. Aucun BER Rayleigh moyen n’est utilisé.
La réalisation Rayleigh unique ne mesure pas la diversité d’un ensemble de canaux.

Les trames sont indépendantes à canal fixé. Les IC à 95 % par ligne utilisent
Clopper-Pearson par porteuse/bit puis Bonferroni ; ils tolèrent les corrélations
entre porteuses d’une même trame dues aux pilotes. Aucune estimation temporelle
partagée, CFO ni défaut de timing n’est introduit dans ce protocole.

Une validation distincte porte sur les essais avec H parfait et CP suffisant :
IC simultanés au moins 99 % sur les références BER par correction de Bonferroni
entre essais. ZF et MMSE ayant les mêmes compteurs, un seul témoin ZF est compté
par essai ; les deux courbes ne constituent pas deux validations indépendantes.

À CP insuffisant, H parfait signifie uniquement « coefficients FIR connus » ;
la multiplication diagonale ne décrit plus exactement le flux reçu. Aucun IC
binomial ni référence diagonale n’est annoncé. Les erreurs et MSE restent descriptives.

## Lecture des graphiques
Les segments relient des points mesurés, sans interpolation de nouveaux résultats.
La grille utilise deux niveaux Eb/N0 ; les balayages fins restent ceux des expériences
précédentes. Le scorecard est une coupe du protocole, pas une recommandation de système.
Le débit est un débit physique de données non codées, hors en-têtes et retransmissions.
