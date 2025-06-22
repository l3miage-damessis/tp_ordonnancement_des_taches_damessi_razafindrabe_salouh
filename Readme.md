# Projet Ordonnancement de Tâches

Ce projet vise à résoudre un problème d’ordonnancement de tâches multi-machines avec contraintes de consommation énergétique et de durée.
## Mise en place de l’environnement

Pour commencer, créez un environnement virtuel Python avec la commande 
```bash
python -m venv venv
```
Activez ensuite cet environnement
Sous Linux/macOS
```bash
source venv/bin/activate
```
Sous Windows PowerShell
```bash
\venv\Scripts\Activate.ps1
```
Une fois activé, installez les dépendances nécessaires avec : 
```bash
pip install -r requirements.txt`
```
Ce fichier inclut notamment `matplotlib` pour les visualisations et `coverage` pour mesurer la couverture des tests.


## Exécution des tests avec coverage

Pour lancer les tests unitaires tout en mesurant la couverture, exécutez :
```bash
python -m coverage run -m unittest discover -s src/scheduling/tests -v
```
Après que les tests ont terminé, générez un rapport HTML avec `coverage html` en executant
```bash
python -m coverage html
```
Ce rapport sera disponible dans le dossier `htmlcov`. Pour consulter les résultats, ouvrez simplement le fichier `htmlcov/index.html` avec un navigateur web.



## Compte Rendu Complet

Le compte rendu complet est disponible dans le fichier [CR.md](./CR.md).  
Veuillez vous référer à ce document pour la modélisation, heuristiques, recherche locale et résultats détaillés.
