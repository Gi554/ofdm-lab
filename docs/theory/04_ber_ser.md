# BER, SER et incertitudes de Monte-Carlo

## Comptage et conventions

Pour N_b bits transmis et E_b^err erreurs, le BER observé est E_b^err/N_b.
Pour N_s symboles et E_s^err symboles contenant au moins un bit faux, le SER est E_s^err/N_s.
Les exposants « err » distinguent les compteurs des énergies Eb et Es.
Un symbole portant k bits donne N_b=k N_s ; BER et SER sont sans unité.
Les symboles sont équiprobables et indépendants, le canal est AWGN, phase et timing idéaux.
L’effectif est choisi **avant** le tirage et jamais arrêté à un nombre d’erreurs.

## Références analytiques

La fonction $Q(x)=\int_x^\infty e^{-t^2/2}dt/\sqrt{2\pi}$ est la queue d’une loi normale standard.
Sa réalisation stable est Q(x)=erfc(x/sqrt(2))/2.
Pour la BPSK et la QPSK Gray cohérentes :

$$P_b=Q(\sqrt{2\gamma_b}),\qquad \gamma_b=10^{(E_b/N_0)_{dB}/10}.$$

En BPSK, Ps=Pb. En QPSK, Ps=2Pb−Pb², car les décisions I et Q sont indépendantes.
La QPSK a le même BER que la BPSK à Eb/N0 fixé, même si elle porte deux bits par symbole.
Ce constat n’affirme pas une même performance à Es/N0 fixé.
Pour une QAM carrée M=L², k=log₂(M), poser
$q=Q(\sqrt{3k\gamma_b/(M-1)})$, puis $p_{axe}=2(1-1/L)q$ :

$$P_s=2p_{axe}-p_{axe}^2.$$

Cette expression de SER est exacte dans le modèle. L’approximation de BER Gray par plus
proches voisins est $P_b\approx4(1-1/L)q/k$. Elle néglige les sauts de plusieurs régions,
donc n’est pas une référence exacte à faible SNR.

## BER QAM exact par transitions gaussiennes

Pour les niveaux normalisés a_r d’un axe et les bornes d_t de ses régions de décision,
avec d_0=−∞ et d_L=+∞ :

$$T_{rt}=\Phi((d_{t+1}-a_r)/\sigma)-\Phi((d_t-a_r)/\sigma),\quad \sigma=\sqrt{N_0/2}.$$

Φ est la fonction de répartition gaussienne standard, σ l’écart-type par axe. Une différence
de fonctions de survie est utilisée dans les queues positives pour éviter la perte de précision.
Si H(g_r,g_t) est la distance de Hamming entre les étiquettes Gray de p=k/2 bits :

$$P_b=\frac{1}{Lp}\sum_{r,t}T_{rt}H(g_r,g_t).$$

Les deux axes identiques portent la même probabilité moyenne par bit. Le calcul tient
compte de tous les sauts ; aucune simulation n’intervient dans cette référence théorique.
En 16-QAM, une vérification indépendante utilise
Pb=3Q(a)/4+Q(3a)/2−Q(5a)/4, a=sqrt(0,8γb).

## Intervalles de confiance

Pour E erreurs Bernoulli sur N essais indépendants, l’intervalle bilatéral Clopper–Pearson
utilise les quantiles bêta : borne basse B⁻¹(α/2;E,N−E+1), borne haute
B⁻¹(1−α/2;E+1,N−E), α=1−confiance. À E=0, la borne basse vaut 0 ; à E=N, la haute vaut 1.
Il est conservateur : sa couverture est au moins le niveau annoncé, sous les hypothèses.
Le SER utilise N_s symboles indépendants.

En QAM, les bits d’un même symbole peuvent être corrélés. Pour le BER, chaque position
binaire j fournit un compteur E_j sur N_s symboles indépendants. Calculer ses bornes CP
avec α/k (Bonferroni) puis moyenner les k bornes basses et hautes donne un intervalle
conservateur de la probabilité moyenne par bit, même en présence de dépendance entre positions.
Il peut être plus large qu’un intervalle supposant tous les bits indépendants.

Une absence d’erreur ne prouve pas Pb=0. Pour zéro erreur **de symbole**, la borne supérieure
unilatérale à confiance c est 1−(1−c)^(1/N_s), environ 3/N_s à 95 %. Le BER étant inférieur
ou égal au SER, cette borne sur Ps borne aussi Pb ; elle ne doit pas être calculée avec N_b
pour une QAM générale. Les graphiques montrent la borne **bilatérale** haute de leur IC,
distincte de cette borne unilatérale.

## Comparaisons multiples

Les 36 points BER et 36 points SER donnent 72 comparaisons. Une enveloppe de validation
utilise α_point=0,01/72 ; la garantie simultanée est donc d’au moins 99 %, par union des
risques, sans exiger l’indépendance entre points. Les graphiques conservent les IC ponctuels
95 % : quelques références hors de ces IC sont possibles et ne constituent pas seules une erreur.
Les tests automatisés utilisent des niveaux conservateurs pour limiter leur fragilité statistique.

## Références vérifiées

- Tse et Viswanath, *Fundamentals of Wireless Communication*, Cambridge University Press,
  2005, [appendice A, détection en bruit gaussien](https://web.stanford.edu/~dntse/Chapters_PDF/Fundamentals_Wireless_Communication_AppendixA.pdf).
- [SciPy : intervalles exacts de proportion](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html),
  méthode Clopper–Pearson et référence bibliographique originale. Consulté le 16 octobre 2026.
La matrice QAM et la correction d’intervalles sont dérivées explicitement ci-dessus.
