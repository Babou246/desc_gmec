### Cachier de charge
[DESC-DIS_FELTRAV SI_DefautsDIS_20210727MajMai2023.docx](https://github.com/Babou246/desc/files/11842068/DESC-DIS_FELTRAV.SI_DefautsDIS_20210727MajMai2023.docx)


## Environnement Virtuel
python3 -m venv env

## Sous Linux
source env/bin/activate

## Lancer l'application avec création automatique des tables
python3 app.py

## Dans app.py ceci va créer les tables
with app.app_context(): '<br>'
    db.create_all()

## Mettre à jour les tables

### Generer l'activativation ou non des clefs
set foreign_key_checks=0;
set foreign_key_checks=1;


## Migration de la base de données
flask dn init

## Si le dossier migrations est présent inutile de faire *flask* *init*
flask db migrate -m "message"
flask db upgrade

### Migration selon la version "a2bc510e80ba" si neccessaire
flask db upgrade a2bc510e80ba

### la base de données
mysqldump -u babou -p desc_users > backup.sql