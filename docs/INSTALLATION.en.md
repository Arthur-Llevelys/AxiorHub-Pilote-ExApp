# Installing AxiorHub Pilote ExApp

> **Development version 0.1.4: for tests only.** Install on a **test server** (virtual machine or test VPS), never first on the firm's
> server. The case described here is a Nextcloud installed directly on the server (Apache, no Docker), with Docker installed next to it
> for ExApps.

## 1. Requirements

- Nextcloud 32 to 35, administrator access, **AppAPI** app enabled (Apps › AppAPI).
- Docker Engine 25 or later on the server: `docker --version`.
- At least 8 GB of memory without local AI; about 2 GB of disk for the image.
- An AI: Ollama on the server or on a firm machine (address reachable from a Docker container), or a pseudonymised external AI set later
  in AxiorHub.

## 2. Install HaRP and register the daemon

HaRP is the Nextcloud proxy that drives Docker for ExApps. The commands below follow the Nextcloud administration manual (“Deployment
configurations”, case “Nextcloud and Docker on the same host - with Nextcloud bare metal”).

```bash
sudo mkdir -p /opt/appapi-harp/certs
sudo docker run \
  -e HP_SHARED_KEY="a_long_secret_key" \
  -e NC_INSTANCE_URL="https://cloud.your-firm.example" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/appapi-harp/certs:/certs \
  --name appapi-harp -h appapi-harp \
  --restart unless-stopped \
  -p 127.0.0.1:8780:8780 -p 127.0.0.1:8782:8782 \
  -d ghcr.io/nextcloud/nextcloud-appapi-harp:release
```

Then redirect Apache's `/exapps/` to HaRP: follow the “Configuring Your Reverse Proxy” section of the
[HaRP README](https://github.com/nextcloud/HaRP), and reload Apache (`sudo systemctl reload apache2`).

In Nextcloud: **Administration settings › AppAPI › Register daemon**, template **“HaRP Proxy (Host)”**: HaRP host `127.0.0.1:8780`, the
same shared key, the Nextcloud address, FRP server `127.0.0.1:8782`. Click “Check connection”, “Register”, then, in the daemon's ⋯ menu,
**“Test deploy”**: it must succeed before going further.

## 3. Prepare the Nextcloud accounts

1. Create the groups `axiorhub-avocats`, `axiorhub-collaborateurs` and `axiorhub-assistants`, and add the members of the firm. Nextcloud
   administrators are AxiorHub administrators; a user without one of these groups has no access.
2. Create the **service user** `axiorhub` (or another name, given at installation) and share the case-files folder with it, for example
   `/Dossiers`. AxiorHub reads and writes files and calendars on its behalf, without an app password.

## 4. Install the ExApp

From the App Store (once the ExApp is published there): **Apps › AxiorHub Pilote › Download and enable**.

Meanwhile, or to choose the settings, on the command line:

```bash
cd /path/to/nextcloud
sudo -u www-data php occ app_api:app:register axiorhub <daemon-name> \
  --info-xml https://github.com/Arthur-Llevelys/AxiorHub-Pilote-ExApp/raw/v0.1.4/appinfo/info.xml \
  --env AXIORHUB_SERVICE_USER=axiorhub \
  --env AXIORHUB_NEXTCLOUD_ROOT=/Dossiers \
  --env AXIORHUB_OLLAMA_URL=http://192.168.1.20:11434 \
  --wait-finish
```

Only the variables declared in `appinfo/info.xml` are taken into account: service user, case-files folder, Ollama address, names of the
three groups.

## 5. First settings

Open **AxiorHub Pilote** in the Nextcloud top menu. In **Settings › Connections**: mailbox (IMAP), AI address and model, calendars; each
section has its own test button. Start in **observation** mode (nothing is written), then switch to **drafts** mode.

## 6. Update, back up, uninstall

- **Update**: Apps › Updates, or `occ app_api:app:update axiorhub`. The `nc_app_axiorhub_data` volume is kept.
- **Backup**: back up the Docker volume `nc_app_axiorhub_data` (firm data: encrypt the copy, keep it off the server).
- **Uninstall**: `occ app_api:app:unregister axiorhub`. **Never** add `--rm-data` without a backup: it erases the volume and all AxiorHub data.

## 7. Troubleshooting

| Symptom | What to do |
|---|---|
| “Heartbeat check failed” during installation | HaRP cannot reach the container: check Apache's `/exapps/` redirection, the shared key and “Test deploy” |
| “Access to AxiorHub Pilote not allowed” page | add the user to one of the AxiorHub groups |
| Case files or calendars not reachable | check the service user and the sharing of the case-files folder |
| AI not reachable | give an Ollama address reachable from a container (firm network address, not `127.0.0.1`) |
| Logs | `sudo docker logs nc_app_axiorhub`; task logs in the volume (`axiorhub/logs`) |

## 8. Migration from the server version

Planned in a later version (export of the server installation, import into the volume, check, switch-over and rollback). Meanwhile, keep
the server version for your firm's work.
