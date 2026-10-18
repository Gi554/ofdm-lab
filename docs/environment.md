# Environnement et reproductibilité

Prérequis : Python 3.11 ou ultérieur et un environnement virtuel isolé.
Suivre le guide d’installation du README ; aucune dépendance à un outil d’assistance
ou à un équipement radio externe n’est nécessaire.

Les premières expériences ont été exécutées sous Windows avec Python 3.12.14 et NumPy
2.5.4. Les versions résolues sont conservées dans requirements-lock.txt : cet inventaire
correspond à Windows/Python 3.12, sans garantie de portabilité de tous les paquets transitifs.
Pour une autre plateforme, installer avec pyproject.toml. La graine et la version NumPy
figurent dans les exports JSON. Le notebook a été exécuté directement cellule par cellule
avec Python ; son démarrage dans un noyau Jupyter interactif n’a pas encore été vérifié.

L’interface a été vérifiée avec Streamlit1.66.0 sous Windows/Python3.12. La CI installe
les extras dev et app pour exécuter les scénarios AppTest sur les trois versions Python.
La surveillance automatique du code est désactivée : redémarrer après une modification.
