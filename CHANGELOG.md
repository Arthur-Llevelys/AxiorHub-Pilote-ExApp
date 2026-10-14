# Journal des versions — AxiorHub Pilote ExApp

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
