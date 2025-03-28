# Projet Enron : Visualisation et analyse des e-mails

## Contexte

L'affaire Enron est un des plus grands scandales financiers des États-Unis, mettant en lumière des pratiques de manipulation comptable et financière qui ont conduit à la faillite de l'entreprise en 2001. Au cœur de cette affaire, des milliers d'e-mails échangés entre les employés d'Enron ont servi d'indice pour comprendre les dynamiques internes de l'entreprise et l'implication de ses dirigeants.

Ce projet vise à implémenter une application web permettant de visualiser et analyser les informations contenues dans les e-mails échangés entre les employés d'Enron, ainsi que de faciliter l'exploration de la base de données des messages. Le projet se concentrera sur l'analyse des interactions, des relations et des événements clés qui ont conduit à ce scandale.

## Objectifs du projet

L’objectif principal est l'implémentation d’une application web pour visualiser des informations pertinentes contenus les e-mails échangés entre les employés d’Enron (dont quelques externes).
Un deuxième objectif est le développement d’un script d’automatisation du peuplement de la base de données, à partir des fichiers (texte plain) contenus dans le jeu de données (20 Go approximativement).

## Installation

Voici comment installer le projet.

### Étape 1 : Installation de Python
Tout d'abord, il faut que vous ayez Python d'installé.
Vous pouvez le vérifier en tapant dans un terminal :
```python --version```

Si vous voyez la version s'afficher, passez directement à l'étape 2.

Sinon téléchargez-le sur le site officiel : [Python Download](https://www.python.org/downloads/)

### Étape 2 : Installation de Django

Installez Django avec pip :

- Linux / macOS:
   ```bash
   python -m pip install Django==5.1.6
   ```

- Windows:
   ```bash
   py -m pip install Django==5.1.6
   ```

### Étape 3 : Téléchargement du projet

Pour cette étape vous avez le choix entre :
- Méthode 1 : Cloner le projet avec git en faisant 

   ```
   git clone https://github.com/vasccla/lp2425_projet2_enron.git
   ```

- Méthode 2 : Télécharger le zip via Github en cliquant sur le bouton **Code** > **Download ZIP**, puis extraire le zip.

### Étape 4 : Installation des modules et librairies

Voici tous les modules / librairies à installer pour que le projet fonctionne, avec la commande correspondante :
- **psycopg** : 

   ```bash
   pip install "psycopg[binary]"
   ```
- **nltk** :

   ```bash
   pip install nltk
   ```
- **dateutil** :

   ```bash
   pip install python-dateutil
   ```
- **rest framework** :

   ```bash
   pip install djangorestframework
   ```

### Étape 5 : Téléchargement des données d'Enron

***À compléter***


## Configuration de la base de données

Pour avoir, en local, la même base de données que celle utilisée par le projet Django, voici comment procéder :

### Étape 1 : Télécharger PostgreSQL

- Rendez-vous sur le site officiel : [PostgreSQL Download](https://www.postgresql.org/download/).
- Sélectionnez votre système d'exploitation.
- Cliquez sur **Download the installer**
- Prenez la version 17.2
1. Lancez le fichier téléchargé pour démarrer l'installation.
2. Suivez les étapes de l'assistant :
   - **Chemin d’installation** : Laissez celui par défaut
   - **Composants à installer** : Laissez cochés "PostgreSQL Server", "pgAdmin 4", et "Command Line Tools".
   - **Mot de passe utilisateur "postgres"** : Saisissez `postgres`
   - **Port** : Par défaut, `5432`.
3. Terminez l'installation.

### Étape 2 : Vérifier l'installation
- Ouvrez un terminal et tapez :
  `psql --version`
- Si PostgreSQL est bien installé, la version sera affichée.
- Sinon, il faudra ajouter PostgreSQL au PATH (voir ci-dessous)

### Étape 3 : Ajouter PostgreSQL au PATH (si nécessaire)

1. Sur Windows, accédez aux **Variables d'environnement** :
   - Dans la barre de recherche Windows, tapez `Variables d'environnement` puis Entrée
   - Allez dans l'onglet **Variables d'environnement**
2. Modifiez la variable `Path` dans les **Variables système** :
   - Ajoutez le chemin vers le dossier `bin` de PostgreSQL (là où est situé le fichier `psql.exe`), par exemple :
    `C:\Program Files\PostgreSQL\17\bin`
3. Validez et redémarrez votre terminal pour appliquer et tester les changements. La commande `psql --version` devrait afficher la version de PostgreSQL.

### Étape 4 : Création de la base de données
Connectez vous à PostgreSQL en tapant `psql -U postgres`
   - Mot de passe : `postgres`

Créez la base de données avec `create database enron;`
   - Tapez `\l` pour vérifier si la base est créée


### Étape 5 : Faire la migration depuis le projet Django

- Placez vous en ligne de commandes dans le projet Django et tapez ``python manage.py migrate`` pour appliquer toutes les migrations à votre base de données locale.
- Vérifiez la création des tables en ouvrant pgAdmin 4 et en allant dans **Server** > **PostgreSQL 17** > **Databases** > **enron** > **Schemas** > **public** > **Tables**
- Ou bien en ligne de commandes `psql -U postgres`
   - Mot de passe : `postgres`
   - Tapez `\c enron`
   - Puis `\d`


## Script de peuplement

Le script de peuplement, créé en tant que commande Django, est exécutable (en se positionnant dans le projet) de la manière suivante :

```bash
python manage.py settlement
```

Il permet d'insérer les données  initiales dans la base de données.

Si vous ne vous voulez l'éxécuter que sur un dossier de mails en particulier, tapez :

```bash
python manage.py settlement --folder nom-dossier
```

Vous pouvez spécifier plusieurs dossiers en les séparant par des espaces : 

```bash
python manage.py settlement --folder dossier1 dossier2 dossier3
```

## Contribution

Pour contribuer au projet, il est important de respecter la convention de nommage des commits.
Ceux-ci seront écrits sous cette forme : `<type>: <description>` de manière à respecter [ceci](https://www.conventionalcommits.org/en/v1.0.0/).

Ci-dessous un tableau résumant les différents types de commits en fonction des cas possibles :

| Commit Type  | Title                    | Description                                                                                                 |
|:------------:|--------------------------|-------------------------------------------------------------------------------------------------------------|
|    `feat`    | Features                 | A new feature                                                                                               |
|     `fix`    | Bug Fixes                | A bug fix                                                                                                   |
|    `docs`    | Documentation            | Documentation only changes                                                                                  |
|   `style`    | Styles                   | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)      |
|  `refactor`  | Code Refactoring         | A code change that neither fixes a bug nor adds a feature                                                   |
|    `perf`    | Performance Improvements | A code change that improves performance                                                                     |
|    `test`    | Tests                    | Adding missing tests or correcting existing tests                                                           |
|    `build`   | Builds                   | Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)         |
|     `ci`     | Continuous Integrations  | Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs) |
|    `chore`   | Chores                   | Other changes that don't modify src or test files                                                           |
|   `revert`   | Reverts                  | Reverts a previous commit                                                                                   |
