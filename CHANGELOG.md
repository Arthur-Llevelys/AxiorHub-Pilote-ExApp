# Journal des versions — AxiorHub Pilote ExApp

## 0.1.6 — moteur AxiorHub Pilote 5.6.47

- Moteur 5.6.47 (correctif) : la génération locale (Ollama) se fait en flux ; une longue réponse, comme la fiche d’un gros dossier, n’est plus coupée au bout de 240 s tant que le modèle écrit. Détail : `CHANGELOG.md` du dépôt AxiorHub-Pilote.

## 0.1.5 — moteur AxiorHub Pilote 5.6.46

- Moteur 5.6.46 (correctif) : le rapprochement des courriels et l’actualisation de l’agenda ne tiennent plus la base en écriture pendant des minutes (lectures IMAP et calculs faits avant d’écrire). Détail : `CHANGELOG.md` du dépôt AxiorHub-Pilote.

## 0.1.4 — moteur AxiorHub Pilote 5.6.45

- Moteur 5.6.45 (correctif) : le worker attend et reprend quand la base est occupée pendant sa boucle, au lieu de s’arrêter ; un travail resté « en cours » est rendu à la file. Détail : `CHANGELOG.md` du dépôt AxiorHub-Pilote.

## 0.1.3 — moteur AxiorHub Pilote 5.6.44

- Moteur 5.6.44 : démarrage tolérant au verrou de la base (les services attendent au lieu de s’arrêter en boucle), test d’affichage de Talk conforme aux navigateurs, corrections de l’audit 5.6.43 (arrêt des appels au modèle, pause reprenable, classement des courriels : autorisations relues, progression de la boîte, mandats durables, nouvelle tentative, dérivés versionnés), corrections de l’avocat dans la page du dossier (parties, juridiction, numéro de RG). Détail : `CHANGELOG.md` et `CONFORMITE-5.6.44.md` du dépôt AxiorHub-Pilote.
- Migrations 0645 (mandats de classement) et 0646 (corrections du dossier) appliquées au démarrage, dans le volume.

## 0.1.2 — moteur AxiorHub Pilote 5.6.43

- Moteur 5.6.43 : « Pause de l’IA » fiable (travaux suspendus puis repris, appel au modèle coupé), aucun brouillon adressé au cabinet lui-même, compétences choisies par phase, classement des courriels et de leurs pièces jointes dans le dossier client (CORRESPONDANCES, NOS PIECES), Agenda en ligne et Agenda personnel séparés, page Talk facultative, Playbooks repris étape par étape, menu sans doublons, cartes « Produire » lisibles. Détail : `CHANGELOG.md` et `CONFORMITE-5.6.43.md` du dépôt AxiorHub-Pilote.
- Dans l’ExApp, AxiorHub et Talk sont servis par la même origine Nextcloud : `X-Frame-Options: SAMEORIGIN` ne devrait pas bloquer la page Talk (à confirmer lors de l’essai d’installation par HaRP).
- Migrations 0643 (contrôle d’arrêt des travaux) et 0644 (courriels conservés) appliquées au démarrage, dans le volume.

## 0.1.1 — correction de la construction de l'image (moteur AxiorHub Pilote 5.6.42)

- L'image 0.1.0 ne se construisait pas : l'installation de `waitress` et `cryptography` partait du dossier source du moteur, supprimé juste avant (`OSError: No such file or directory`). La construction quitte maintenant ce dossier avant de le supprimer. Aucune image 0.1.0 n'a été publiée.

## 0.1.0 — version de développement (moteur AxiorHub Pilote 5.6.42)

Première version, issue du cahier des charges « AxiorHub Pilote ExApp » (lots L1 et L2, L3 en partie). Pour des tests seulement.

- **Conditionnement AppAPI** : manifeste `appinfo/info.xml` (identifiant `axiorhub`, image `ghcr.io/arthur-llevelys/axiorhub-exapp`,
  version égale à l'étiquette de l'image, routes : icône publique, tout le reste réservé aux utilisateurs connectés, cookies non transmis ;
  variables : utilisateur de service, dossier des dossiers clients, adresse d'Ollama, groupes), `Dockerfile` Alpine 3.21 (moteur construit
  depuis son tag publié, LibreOffice, Tesseract français, Poppler, eSpeak NG, polices, `frp`), script HaRP `start.sh` du modèle de
  référence de Nextcloud, contrôle de santé.
- **Moteur 5.6.42, mode ExApp** (`agent/exapp5642.py`, point d'entrée `exapp.py`) : battement, initialisation avec progression,
  activation (entrée du menu supérieur et script de la page), contrôle des en-têtes AppAPI à temps constant, rôles par groupes Nextcloud,
  droits de la distribution autonome, pages affichées dans Nextcloud (même origine), Nextcloud (WebDAV, CalDAV, Deck, Talk) par les
  en-têtes AppAPI au nom de l'utilisateur de service, installation idempotente dans le volume persistant, travaux et veille supervisés.
- **Paquet de la boutique** reproductible (`scripts/build-appstore-package.py`), contrôles du dépôt (`tests/test_package.py`), recette
  GitHub (contrôles, image, publication sur ghcr.io pour un tag), documentation française et anglaise.
