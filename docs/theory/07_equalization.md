# Égalisation connue : ZF, MMSE et décisions

Le modèle scalaire par porteuse est Y=HX+W, valable après retrait d’un CP suffisant.
H est connu parfaitement ; E|X|²=Es=1 et E|W|²=N0. Toutes les amplitudes et énergies
sont normalisées ; les retards restent des nombres d’échantillons.

## Poids, erreur quadratique et biais

ZF applique $A_{ZF}=1/H$. L’estimation est non biaisée et sa variance de bruit vaut
N0/|H|². Un creux profond amplifie le bruit. Le code refuse d’inverser un module <=1e-12,
au lieu de masquer une singularité par un epsilon modifiant le canal.

Pour une estimation linéaire AX, plus précisément $\hat X=AY$, la MSE est
$E_s|AH-1|^2+N_0|A|^2$. Sa minimisation donne

$$A_{MMSE}=\frac{H^*}{|H|^2+N_0/E_s},\qquad
G=A_{MMSE}H=\frac{|H|^2}{|H|^2+N_0/E_s}.$$

La MSE minimale vaut Es N0/(Es|H|²+N0). Le MMSE régularise les creux mais produit une
estimation biaisée de moyenne conditionnelle G X. La variance de bruit en sortie vaut
|A|² N0. Le gain G doit accompagner les valeurs estimées. Pour H nul, le MMSE renvoie
une estimation 0 et un indicateur d’effacement : aucune information n’est récupérée.

## Estimation et détection ne sont pas la même tâche

Avec H non nul et N0 connu, $A_{MMSE}=G A_{ZF}$, avec G réel positif. Décider contre
l’alphabet réduit G X est équivalent à décider sur $\hat X/G=Y/H$. Ainsi les décisions
ZF et MMSE avec gain pris en compte sont identiques dans ce modèle **scalaire** connu.
Cela n’empêche pas le MMSE d’avoir une MSE d’estimation plus faible.
Décider la QAM MMSE avec les seuils de l’alphabet non réduit conserve un biais et peut
augmenter le BER. Le mode `raw` sert explicitement à étudier cette erreur de seuils ;
il n’est pas le mode par défaut. Ce résultat n’est pas une affirmation sur tous les
récepteurs MMSE vectoriels ou canaux inconnus.

## Modèles conditionnels et incertitudes

À canal fixé, Eb/N0 effectif sur la porteuse i vaut
$(Eb/N0)_{i,dB}=(Eb/N0)_{utile,dB}+10\log_{10}|H_i|^2$.
Le BER/SER ZF (ou MMSE à décisions adaptées) est la moyenne des références AWGN aux
rapports effectifs des K porteuses. Ce sont des références conditionnelles à H, pas une
moyenne de performances sur une loi Rayleigh. Le bruit est calibré à l’émetteur ; le canal
et la puissance reçue ne sont jamais renormalisés après tirage.

Les probabilités d’erreur diffèrent entre porteuses. Additionner leurs erreurs puis utiliser
un IC binomial homogène serait injustifié. Chaque compteur par porteuse/bit suit une loi
binomiale sur les trames iid lorsque le CP suffit. Les bornes Clopper–Pearson avec Bonferroni,
puis leur moyenne, bornent la probabilité moyenne ; les IC sont conservateurs. Pour le SER,
la stratification est par porteuse. Pour CP court, aucune référence diagonale ni IC binomial
n’est annoncé, car l’interférence crée une dépendance entre trames.

Référence : Tse et Viswanath, *Fundamentals of Wireless Communication*, Cambridge, 2005,
[chapitre 3](https://web.stanford.edu/~dntse/Chapters_PDF/Fundamentals_Wireless_Communication_chapter3.pdf),
et [appendice A](https://web.stanford.edu/~dntse/Chapters_PDF/Fundamentals_Wireless_Communication_AppendixA.pdf).
Les poids scalaires, les gains et la stratification sont explicités ci-dessus.
