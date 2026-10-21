# Installer AxiorHub Pilote ExApp

> **Version de développement 0.1.28 : pour des tests seulement.** Faites l'installation sur un **serveur d'essai** (machine virtuelle ou
> VPS de test), jamais d'abord sur le serveur du cabinet. Le cas décrit ici est celui d'un Nextcloud installé directement sur le serveur
> (Apache, sans Docker), avec Docker installé à côté pour les ExApps.

## 1. Prérequis

- Nextcloud 32 à 35, accès administrateur, application **AppAPI** activée (Applications › AppAPI).
- Docker Engine 25 ou plus sur le serveur : `docker --version`.
- 8 Go de mémoire au moins sans IA locale ; environ 2 Go de disque pour l'image.
- Une IA : Ollama sur le serveur ou une machine du cabinet (adresse joignable depuis un conteneur Docker), ou une IA externe
  pseudonymisée réglée ensuite dans AxiorHub.

## 2. Installer HaRP et enregistrer le démon

HaRP est le mandataire de Nextcloud qui pilote Docker pour les ExApps. Les commandes ci-dessous suivent la documentation d'administration
de Nextcloud (« Deployment configurations », cas « Nextcloud and Docker on the same host - with Nextcloud bare metal »).

```bash
sudo mkdir -p /opt/appapi-harp/certs
sudo docker run \
  -e HP_SHARED_KEY="une_cle_longue_et_secrete" \
  -e NC_INSTANCE_URL="https://cloud.votre-cabinet.fr" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/appapi-harp/certs:/certs \
  --name appapi-harp -h appapi-harp \
  --restart unless-stopped \
  -p 127.0.0.1:8780:8780 -p 127.0.0.1:8782:8782 \
  -d ghcr.io/nextcloud/nextcloud-appapi-harp:release
```

Redirigez ensuite `/exapps/` d'Apache vers HaRP : suivez la section « Configuring Your Reverse Proxy » du
[README de HaRP](https://github.com/nextcloud/HaRP), puis rechargez Apache (`sudo systemctl reload apache2`).

Dans Nextcloud : **Paramètres d'administration › AppAPI › Enregistrer un démon**, modèle **« HaRP Proxy (Host) »** : hôte HaRP
`127.0.0.1:8780`, même clé partagée, adresse de Nextcloud, serveur FRP `127.0.0.1:8782`. Cliquez « Check connection », « Register »,
puis, dans le menu ⋯ du démon, **« Test deploy »** : il doit réussir avant d'aller plus loin.

## 3. Préparer les comptes Nextcloud

1. Créez les groupes `axiorhub-avocats`, `axiorhub-collaborateurs` et `axiorhub-assistants`, et ajoutez-y les membres du cabinet. Les
   administrateurs de Nextcloud sont administrateurs d'AxiorHub ; un utilisateur sans l'un de ces groupes n'a aucun accès.
2. Créez l'**utilisateur de service** `axiorhub` (ou un autre nom, indiqué à l'installation) et partagez-lui le dossier des dossiers
   clients, par exemple `/Dossiers`. AxiorHub lit et dépose les fichiers et les agendas en son nom, sans mot de passe d'application.

## 4. Installer l'ExApp

Depuis la boutique (quand l'ExApp y est publiée) : **Applications › AxiorHub Pilote › Télécharger et activer**.

En attendant, ou pour choisir les réglages, en ligne de commande :

```bash
cd /chemin/vers/nextcloud
sudo -u www-data php occ app_api:app:register axiorhub <nom-du-démon> \
  --info-xml https://github.com/Arthur-Llevelys/AxiorHub-Pilote-ExApp/raw/v0.1.28/appinfo/info.xml \
  --env AXIORHUB_SERVICE_USER=axiorhub \
  --env AXIORHUB_NEXTCLOUD_ROOT=/Dossiers \
  --env AXIORHUB_OLLAMA_URL=http://192.168.1.20:11434 \
  --wait-finish
```

Seules les variables déclarées dans `appinfo/info.xml` sont prises en compte : utilisateur de service, dossier des dossiers clients,
adresse d'Ollama, noms des trois groupes.

## 5. Premier réglage

Ouvrez **AxiorHub Pilote** dans le menu supérieur de Nextcloud. Dans **Paramètres › Connexions** : messagerie (IMAP), adresse et modèle
de l'IA, agendas ; chaque rubrique a son bouton de test. Commencez en mode **observation** (rien n'est écrit), puis passez en mode
**brouillons**.

## 6. Mettre à jour, sauvegarder, désinstaller

- **Mise à jour** : Applications › Mises à jour, ou `occ app_api:app:update axiorhub`. Le volume `nc_app_axiorhub_data` est conservé.
- **Sauvegarde** : sauvegardez le volume Docker `nc_app_axiorhub_data` (données du cabinet : chiffrez la copie, gardez-la hors du serveur).
- **Désinstallation** : `occ app_api:app:unregister axiorhub`. N'ajoutez **jamais** `--rm-data` sans sauvegarde : cette option efface le
  volume et toutes les données d'AxiorHub.

## 7. En cas de difficulté

| Constat | Que faire |
|---|---|
| « Heartbeat check failed » à l'installation | HaRP n'atteint pas le conteneur : vérifiez la redirection `/exapps/` d'Apache, la clé partagée et « Test deploy » |
| Page « Accès à AxiorHub Pilote non autorisé » | ajoutez l'utilisateur à l'un des groupes AxiorHub |
| Dossiers ou agendas inaccessibles | vérifiez l'utilisateur de service et le partage du dossier des dossiers clients |
| IA injoignable | indiquez une adresse d'Ollama joignable depuis un conteneur (adresse du réseau du cabinet, pas `127.0.0.1`) |
| Journaux | `sudo docker logs nc_app_axiorhub` ; journaux des travaux dans le volume (`axiorhub/logs`) |

## 8. Migration depuis la version serveur

Prévue dans une version ultérieure (export de l'installation serveur, import dans le volume, contrôle, bascule et retour arrière). D'ici
là, gardez la version serveur pour le travail du cabinet.
