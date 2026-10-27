# Hopbeliard Guide Utilisateur

## Configuration de l'App

Créez un fichier `.conf` sur le modèle du `.conf.exemple`

```
#===APP PARAMETERS===

# supported "sqlite", "mysql", "mariadb", "postgresql"
DB_FORMAT = "sqlite"
DB_NAME = "local_db"
DB_HOST = ""
DB_PORT = ""
DB_USER = ""
DB_PASSWORD = ""

#secret key for flask app, empty for random key
APP_SECRET = ""

CLEANUP_INTERVAL = 60
CHALLENGE_TTL = 3

#host for flask app and port
HOST = 0.0.0.0
PORT = 8090
```

**Lors du premier lancement utiliser la commande `python server.py --reset_admin_password <mot_de_passe>`**
L'utilisateur par defaut est *admin*

## Pannel Administration

Pour créer un utilisateur, il vous suffit de renseigner son identifiant (unique) et de sélectionner ses droits. Un mot de passe provisoire est fourni lors de la création du compte.

Vous pouvez également désactiver un compte, régénérer son mot de passe ou supprimer le compte.

## Pannel Patients

Les utilisateurs disposant des droits **LECTURE_PATIENT** et **EDITION_PATIENT** peuvent accéder à ce panneau et, respectivement, consulter ou modifier les données des patients.

Pour créer un patient, il suffit de renseigner son nom et son prénom.

Pour ajouter un événement à un patient, il faut d'abord le sélectionner à l'aide du bouton select dans le tableau. Il est ensuite possible d'ajouter un événement à l'aide du formulaire situé en bas de la page.


