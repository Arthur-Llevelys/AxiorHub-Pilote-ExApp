# AxiorHub Pilote ExApp

[Français](README.md) · **English**

A **standalone** Nextcloud app: the AxiorHub Pilote engine — legal software designed for French lawyers (avocats) — shipped in a container
managed by Nextcloud (AppAPI). Installed from the Nextcloud App Store, one login (the Nextcloud account), updates from the App Store, data in
a persistent volume.

> **Development version 0.1.0 — for tests only, not for production yet.** The AppAPI contract is tested, but the real installation
> through HaRP and the migration from a server installation still have to be qualified (see “Status” below). For your firm's work, use the
> [AxiorHub server version](https://github.com/Arthur-Llevelys/AxiorHub-Pilote) and the
> [AxiorHub Pilote for Nextcloud](https://github.com/Arthur-Llevelys/AxiorHub-Pilote-Nextcloud) app in the meantime.

## What the ExApp does

- Nextcloud installs, starts, updates and removes the AxiorHub container (AppAPI, HaRP daemon).
- The **AxiorHub Pilote** entry of the Nextcloud top menu shows the AxiorHub interface (Today, cases, emails, calendar, Produce,
  Corporate, Pilot…), served on the Nextcloud domain (`/exapps/axiorhub/`): no AxiorHub password, no account linking, no third-party cookie.
- **Rights through Nextcloud groups**: `axiorhub-avocats` and `axiorhub-collaborateurs` → lawyer, `axiorhub-assistants` → assistant,
  Nextcloud administrators → administrator. No group: no access. The rights per role are those of the AxiorHub standalone distribution
  (checked on every request).
- Case files and calendars are read and written **on behalf of a Nextcloud service user** (`axiorhub` by default), without an app password.
- Background tasks, mailbox watching and agent runs work inside the container, monitored and restarted.

## Architecture

```
Browser ── Nextcloud session ──> Apache + Nextcloud ──/exapps/axiorhub/──> HaRP ──FRP tunnel──> AxiorHub container
                                                                                                ├─ AppAPI gateway (/tmp/exapp.sock socket)
                                                                                                ├─ AxiorHub interface (existing engine)
                                                                                                ├─ tasks · IMAP watching · agent runs
                                                                                                └─ persistent volume (state, index, configuration)
Container ──> Nextcloud (OCS, WebDAV, CalDAV with the AppAPI headers) · Ollama or pseudonymised external AI · IMAP/SMTP mailbox
```

**One engine code base.** This repository holds the **packaging**: `appinfo/info.xml` manifest, `Dockerfile`, HaRP `start.sh` script,
App Store package, tests, documentation. The gateway and the ExApp mode are part of the engine
([`agent/exapp5642.py`](https://github.com/Arthur-Llevelys/AxiorHub-Pilote/blob/main/agent/exapp5642.py), entry point `exapp.py`) and are
tested by its suite (`ExApp` class of `tests/test_v5642.py`). The image is built from the published engine tag given in `ENGINE_VERSION`
(currently 5.6.42).

## Requirements

| Item | Requirement |
|---|---|
| Nextcloud | 32 to 35, **AppAPI** app enabled |
| Deploy daemon | **HaRP** configured by the administrator (see [docs/INSTALLATION.en.md](docs/INSTALLATION.en.md)); “Test deploy” succeeded |
| Docker | Docker Engine 25 or later on the Nextcloud server (or on a machine HaRP can reach) |
| Memory, disk | at least 8 GB without local AI; about 2 GB for the image |
| AI | Ollama (server or firm machine) or an external AI, always pseudonymised |
| Accounts | groups `axiorhub-avocats`, `axiorhub-collaborateurs`, `axiorhub-assistants`; service user `axiorhub`; IMAP settings |

## Installation (summary)

1. Install HaRP and register the daemon (Administration settings › AppAPI), then “Test deploy”.
2. Create the groups and the service user; share the case-files folder with it (`/Dossiers`).
3. App Store: **Apps › AxiorHub Pilote › Download and enable** — or, before the App Store release:

   ```bash
   sudo -u www-data php occ app_api:app:register axiorhub <daemon-name> \
     --info-xml https://github.com/Arthur-Llevelys/AxiorHub-Pilote-ExApp/raw/v0.1.0/appinfo/info.xml \
     --env AXIORHUB_OLLAMA_URL=http://192.168.1.20:11434 --wait-finish
   ```

4. Open **AxiorHub Pilote** in the top menu, then **Settings › Connections**: mailbox, AI, calendars; start in observation mode.

Full guide: [docs/INSTALLATION.en.md](docs/INSTALLATION.en.md).

## Status of version 0.1.0

| Work package | Status |
|---|---|
| L1 — engine ExApp mode (5.6.42) | **Done**: storage in the volume, delegated authentication, roles from groups, Nextcloud through AppAPI, supervisor shared with the workstation version; engine tests green. |
| L2 — image and gateway | **Done, to be qualified**: `Dockerfile`, `start.sh`, lifecycle, headers, repository checks. The real installation through HaRP has not been tried yet (no Docker on the development machine). |
| L3 — Nextcloud integration | **Partly**: top menu, page, roles, service user. Still to do: actions on behalf of the signed-in user (instead of the service user), Nextcloud notifications, administration page. |
| L4 — migration from the server version | **To do** (export and import command). |
| L5 — security, backup, performance | **To do**: review, volume backup procedure, measurements. |
| L6 — publication | **To do**: image on ghcr.io, certificate for the `axiorhub` app id, App Store. |

## Build

```bash
docker build -t ghcr.io/arthur-llevelys/axiorhub-exapp:0.1.0 .
python3 scripts/build-appstore-package.py dist/axiorhub-0.1.0.tar.gz   # App Store package (appinfo folder)
python3 -m unittest discover -s tests                                   # repository checks
```

The GitHub workflow (`.github/workflows/exapp.yml`) runs the checks and builds the image on every push; it publishes the image on ghcr.io
for a `v*` tag.

## Licence

AGPL-3.0-or-later. The `start.sh` script reuses Nextcloud's reference template (AGPL-3.0-or-later, Nextcloud GmbH and Nextcloud
contributors).
