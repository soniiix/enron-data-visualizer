# Projet Enron : Visualisation et analyse des e-mails

## Contexte

L'affaire Enron est un des plus grands scandales financiers des États-Unis, mettant en lumière des pratiques de manipulation comptable et financière qui ont conduit à la faillite de l'entreprise en 2001. Au cœur de cette affaire, des milliers d'e-mails échangés entre les employés d'Enron ont servi d'indice pour comprendre les dynamiques internes de l'entreprise et l'implication de ses dirigeants.

Ce projet vise à implémenter une application web permettant de visualiser et analyser les informations contenues dans les e-mails échangés entre les employés d'Enron, ainsi que de faciliter l'exploration de la base de données des messages. Le projet se concentrera sur l'analyse des interactions, des relations et des événements clés qui ont conduit à ce scandale.

## Objectifs du projet

L’objectif principal est l'implémentation d’une application web pour visualiser des informations pertinentes contenus les e-mails échangés entre les employés d’Enron (dont quelques externes).
Un deuxième objectif est le développement d’un script d’automatisation du peuplement de la base de données, à partir des fichiers (texte plain) contenus dans le jeu de données (20 Go approximativement).

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
