# AxiorHub Pilote ExApp

**Français** · [English](README.en.md)

Application Nextcloud **autonome** : le moteur AxiorHub Pilote — logiciel juridique destiné aux avocats français — livré dans un conteneur
géré par Nextcloud (AppAPI). Installation depuis la boutique Nextcloud, une seule connexion (le compte Nextcloud), mises à jour depuis la
boutique, données dans un volume persistant.

> **Version de développement 0.1.5 — pour des tests seulement, pas encore pour la production.** Le contrat AppAPI est testé, mais
> l'installation réelle par HaRP et la migration depuis une installation serveur restent à qualifier (voir « État » ci-dessous). Pour le
> travail du cabinet, utilisez d'ici là la [version serveur d'AxiorHub](https://github.com/Arthur-Llevelys/AxiorHub-Pilote) et
> l'application [AxiorHub Pilote pour Nextcloud](https://github.com/Arthur-Llevelys/AxiorHub-Pilote-Nextcloud).

## Ce que fait l'ExApp

- Nextcloud installe, démarre, met à jour et supprime le conteneur AxiorHub (AppAPI, démon HaRP).
- L'entrée **AxiorHub Pilote** du menu supérieur de Nextcloud affiche l'interface d'AxiorHub (Aujourd'hui, dossiers, courriels, agenda,
  Produire, Corporate, Pilote…), servie sur le domaine de Nextcloud (`/exapps/axiorhub/`) : aucun mot de passe AxiorHub, aucune liaison
  de compte, aucun cookie tiers.
- **Droits par groupes Nextcloud** : `axiorhub-avocats` et `axiorhub-collaborateurs` → avocat, `axiorhub-assistants` → assistant,
  administrateurs de Nextcloud → administrateur. Sans groupe : aucun accès. Les droits par rôle sont ceux de la distribution autonome
  d'AxiorHub (contrôlés à chaque requête).
- Fichiers des dossiers et agendas lus et déposés **au nom d'un utilisateur de service** Nextcloud (`axiorhub` par défaut), sans mot de
  passe d'application.
- Travaux, veille de la messagerie et passages de l'agent tournent dans le conteneur, surveillés et relancés.

## Architecture

```
Navigateur ── session Nextcloud ──> Apache + Nextcloud ──/exapps/axiorhub/──> HaRP ──tunnel FRP──> conteneur AxiorHub
                                                                                                   ├─ passerelle AppAPI (socket /tmp/exapp.sock)
                                                                                                   ├─ interface AxiorHub (moteur existant)
                                                                                                   ├─ travaux · veille IMAP · passages
                                                                                                   └─ volume persistant (état, index, configuration)
Conteneur ──> Nextcloud (OCS, WebDAV, CalDAV avec les en-têtes AppAPI) · Ollama ou IA externe pseudonymisée · messagerie IMAP/SMTP
```

**Un seul code moteur.** Ce dépôt contient le **conditionnement** : manifeste `appinfo/info.xml`, `Dockerfile`, script HaRP `start.sh`,
paquet de la boutique, tests, documentation. Le code de la passerelle et du mode ExApp fait partie du moteur
([`agent/exapp5642.py`](https://github.com/Arthur-Llevelys/AxiorHub-Pilote/blob/main/agent/exapp5642.py), point d'entrée `exapp.py`) et
est testé par sa suite (classe `ExApp` de `tests/test_v5642.py`). L'image est construite depuis le tag publié du moteur indiqué dans
`ENGINE_VERSION` (actuellement 5.6.46).

## Prérequis

| Élément | Exigence |
|---|---|
| Nextcloud | 32 à 35, application **AppAPI** activée |
| Démon de déploiement | **HaRP** configuré par l'administrateur (voir [docs/INSTALLATION.md](docs/INSTALLATION.md)) ; « Test deploy » réussi |
| Docker | Docker Engine 25 ou plus sur le serveur Nextcloud (ou sur une machine joignable par HaRP) |
| Mémoire, disque | 8 Go au moins sans IA locale ; environ 2 Go pour l'image |
| IA | Ollama (serveur ou machine du cabinet) ou IA externe, toujours pseudonymisée |
| Comptes | groupes `axiorhub-avocats`, `axiorhub-collaborateurs`, `axiorhub-assistants` ; utilisateur de service `axiorhub` ; paramètres IMAP |

## Installation (résumé)

1. Installer HaRP et enregistrer le démon (Paramètres d'administration › AppAPI), puis « Test deploy ».
2. Créer les groupes et l'utilisateur de service ; partager le dossier des dossiers clients avec lui (`/Dossiers`).
3. Boutique : **Applications › AxiorHub Pilote › Télécharger et activer** — ou, avant la publication sur la boutique :

   ```bash
   sudo -u www-data php occ app_api:app:register axiorhub <nom-du-démon> \
     --info-xml https://github.com/Arthur-Llevelys/AxiorHub-Pilote-ExApp/raw/v0.1.5/appinfo/info.xml \
     --env AXIORHUB_OLLAMA_URL=http://192.168.1.20:11434 --wait-finish
   ```

4. Ouvrir **AxiorHub Pilote** dans le menu supérieur, puis **Paramètres › Connexions** : messagerie, IA, agendas ; commencer en mode
   observation.

Guide complet : [docs/INSTALLATION.md](docs/INSTALLATION.md).

## État de la version 0.1.5

| Lot du cahier des charges | État |
|---|---|
| L1 — mode ExApp du moteur (5.6.42) | **Fait** : stockage dans le volume, authentification déléguée, rôles par groupes, Nextcloud par AppAPI, superviseur commun avec la version poste ; tests du moteur verts. |
| L2 — image et passerelle | **Fait, à qualifier** : `Dockerfile`, `start.sh`, cycle de vie, en-têtes, contrôles du dépôt. L'installation réelle par HaRP n'a pas encore été essayée (aucun Docker sur la machine de développement). |
| L3 — intégration Nextcloud | **En partie** : menu supérieur, page, rôles, utilisateur de service. Restent : actions au nom de l'utilisateur connecté (et non de l'utilisateur de service), notifications Nextcloud, page d'administration. |
| L4 — migration depuis la version serveur | **À faire** (commande d'export et d'import). |
| L5 — sécurité, sauvegarde, performance | **À faire** : revue, procédure de sauvegarde du volume, mesures. |
| L6 — publication | **À faire** : image sur ghcr.io, certificat de l'identifiant `axiorhub`, boutique. |

## Construire

```bash
docker build -t ghcr.io/arthur-llevelys/axiorhub-exapp:0.1.5 .
python3 scripts/build-appstore-package.py dist/axiorhub-0.1.5.tar.gz   # paquet de la boutique (dossier appinfo)
python3 -m unittest discover -s tests                                   # contrôles du dépôt
```

La recette GitHub (`.github/workflows/exapp.yml`) exécute les contrôles et construit l'image à chaque envoi ; elle publie l'image sur
ghcr.io pour un tag `v*`.

## Licence et auteur

AGPL-3.0-or-later. Auteur : Timo RAINIO. Le script `start.sh` reprend le modèle de référence de Nextcloud (AGPL-3.0-or-later,
Nextcloud GmbH and Nextcloud contributors).
