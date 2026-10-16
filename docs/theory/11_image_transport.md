# Transport d’image : format, intégrité et mesures

## Pixels et fichier local
Le chargeur accepte un PNG local, converti en RGB8 H×W×3, en ordre ligne par ligne,
pixel par pixel, puis rouge/vert/bleu. Gris devient RGB ; un canal alpha est composé
sur blanc. Les valeurs flottantes lues du PNG sont arrondies vers 0..255.
La limite du laboratoire est 4 MiB de pixels décodés, dimensions non nulles <=65535.
Le PNG n’est pas transmis : seuls ses pixels sont transportés, sans compression.
Les PNG reçus sont créés localement à partir des pixels décodés.

## Paquet binaire version 1
Les entiers d’en-tête sont non signés, ordre réseau big-endian. Les bits de chaque
octet sont émis du plus significatif au moins significatif (unpackbits bitorder=big).
La taille de bloc utile S, publique et fixe sur le lien, est multiple de 3 et <=65535.
Par défaut S=192 octets (64 pixels). Le paquet physique fait 36+S octets.

| Octet initial | Taille | Champ |
|---:|---:|---|
| 0 | 4 | Magic ASCII OFLI |
| 4 | 1 | Version 1 |
| 5 | 1 | Nombre de canaux, 3 |
| 6 | 2 | Largeur |
| 8 | 2 | Hauteur |
| 10 | 4 | Nombre total d’octets RGB |
| 14 | 4 | Numéro de paquet, à partir de zéro |
| 18 | 4 | Nombre total de paquets |
| 22 | 2 | Octets utiles de ce bloc |
| 24 | 4 | CRC32 des octets utiles du bloc |
| 28 | 4 | CRC32 de tous les pixels de l’image |
| 32 | 4 | CRC32 des 32 octets d’en-tête précédents |
| 36 | S | Données RGB puis éventuels zéros de bourrage |

Les CRC sont ceux de zlib.crc32. Les métadonnées sont répétées dans chaque paquet.
Le CRC global sert aussi à distinguer les images de mêmes dimensions ; ce n’est pas
un identifiant sans collision ni une authentification. CRC32 détecte des erreurs,
ne les corrige pas et ne garantit pas la détection de toute corruption possible.

Le dernier bloc transporte min(S, octets restants) et complète à S par des zéros.
Ce bourrage n’entre pas dans le CRC des pixels. Les bits de tous les paquets sont
ensuite complétés à la capacité entière de la dernière trame OFDM. Ces deux bourrages
sont distincts, comptés séparément et jamais présentés comme pixels utiles.

## Réassemblage sans image oracle
Début du burst, frontières de paquets, taille S et longueur de transport sont connus
du lien physique simulé. Aucune synchronisation de paquet aveugle n’est revendiquée.
La longueur programmée permet de retirer le bourrage OFDM ; elle ne donne pas au
décodeur les dimensions ou les pixels originaux.

Un en-tête n’est utilisé qu’après contrôle CRC et cohérence version/dimensions/taille/
séquence. Les limites sont vérifiées avant allocation de l’image. Les en-têtes
contradictoires et séquences dupliquées sont rejetés ; les paquets réordonnés sont
réassemblés. Les paquets manquants ou tronqués restent des effacements.
Aucun en-tête fiable implique aucune image reconstruite, sans recours aux dimensions
originales. Si une métadonnée fiable existe, deux vues sont disponibles :

- **diagnostic** : pixels reçus des paquets à en-tête fiable, même si leur CRC contenu échoue.
- **accepted** : pixels des seuls blocs au CRC valide.

Les positions manquantes sont magenta [255,0,255], avec un masque explicite ; la couleur
seule ne suffit pas à identifier les pertes si l’original contient aussi du magenta.
Quand tous les blocs sont acceptés, le CRC global est vérifié. Les états sont complete,
partial, metadata_only ou unavailable. Un canevas entièrement magenta avec métadonnées
fiables n’est donc pas une transmission réussie.

## Chaîne radio et énergie
Mapping et pilotes, IFFT/CP, convolution sur le flux, AWGN, retrait CP/FFT, estimation
H et égalisation sont les modules déjà validés. Les canaux sont statiques, CFO nul,
timing connu. Les modes sans correction, H parfait et H estimé utilisent le même bruit.
Il n’y a ni codage correcteur, entrelacement, ARQ ni protection renforcée des en-têtes.

La référence Eb/N0 est **nominale par bit de données OFDM transportées**, incluant
pilotes et CP avec l’hypothèse d’alphabet équiprobable Es=1. Les données transportées
comprennent les en-têtes, les pixels et les bourrages. Une image et ses en-têtes ne
sont pas iid : surtout en QAM, leur énergie réalisée peut différer de ce budget nominal.
L’expérience publie donc l’énergie totale réellement émise, puis par bit de transport
physique et par bit d’image. Aucune renormalisation ad hoc du fichier ou du signal reçu
n’est appliquée. Les énergies sont en unités normalisées, pas des joules RF calibrés.

## Compteurs scientifiques
Le simulateur compare les bits programmés aux décisions pour mesurer le BER transport,
les erreurs d’en-têtes, de pixels et de bourrage. Le BER pixels et les octets RGB erronés
bruts sont mesurés aux positions programmées, même si les en-têtes correspondants ont
été perdus. Cette connaissance oracle appartient à la mesure, pas au décodeur d’image.
Les vues ne récupèrent pas ces blocs perdus grâce à ce compteur.

Les erreurs d’image reconstruite incluent les valeurs de remplacement ; on publie
séparément octets effacés, erreurs des octets acceptés et CRC. BER radio, fraction de
blocs acceptés et apparence visuelle sont trois mesures différentes.
Les BER de cette image déterministe restent descriptifs : aucun IC binomial ni
comparaison à un BER théorique iid n’est revendiqué. Les mêmes pixels sont répétés
entre essais ; les totaux ne sont pas annoncés comme des bits source distincts.

Une corruption de RGB brut n’imite pas celle d’un fichier PNG/JPEG comprimé, d’un codec
vidéo, d’une liaison RF physique ou d’un système doté de retransmissions. Un bit de
poids fort peut produire un changement de couleur bien plus visible qu’un bit faible.
