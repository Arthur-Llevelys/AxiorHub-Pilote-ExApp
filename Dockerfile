# SPDX-License-Identifier: AGPL-3.0-or-later
# AxiorHub Pilote ExApp : moteur AxiorHub Pilote dans un conteneur géré par AppAPI (Nextcloud 32 à 35, démon HaRP).
# Alpine 3.21 fournit frp, exigé par start.sh pour le tunnel HaRP (voir https://github.com/nextcloud/HaRP, « Adapting ExApps to use HaRP »).
FROM alpine:3.21

# Version du moteur : un tag publié du dépôt AxiorHub-Pilote (le même que dans ENGINE_VERSION).
ARG AXIORHUB_VERSION=5.6.80
ARG AXIORHUB_REPOSITORY=https://github.com/Arthur-Llevelys/AxiorHub-Pilote.git

LABEL org.opencontainers.image.title="AxiorHub Pilote ExApp" \
      org.opencontainers.image.source="https://github.com/Arthur-Llevelys/AxiorHub-Pilote-ExApp" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later" \
      org.opencontainers.image.description="Moteur AxiorHub Pilote pour Nextcloud (AppAPI)"

RUN apk add --no-cache bash curl frp python3 py3-pip git tini \
        poppler-utils tesseract-ocr tesseract-ocr-data-fra espeak-ng \
        libreoffice-writer font-dejavu font-liberation

# Moteur : archive vérifiée construite depuis le tag publié (manifeste d'empreintes contrôlé par le script de construction).
RUN git clone --depth 1 --branch "v${AXIORHUB_VERSION}" "${AXIORHUB_REPOSITORY}" /tmp/axiorhub-src \
    && cd /tmp/axiorhub-src \
    && python3 scripts/build-release.py /tmp/axiorhub.tar.gz \
    && mkdir -p /app \
    && tar -xzf /tmp/axiorhub.tar.gz -C /app --strip-components=1 \
    && cd / \
    && rm -rf /tmp/axiorhub-src /tmp/axiorhub.tar.gz \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir waitress==3.0.2 cryptography==44.0.0 \
    && apk del git

COPY --chmod=755 start.sh /start.sh
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1

# Contrôle de santé : socket HaRP ou port direct. AppAPI attend un conteneur sain pendant l'installation.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=20s --start-interval=2s \
    CMD sh -c 'curl -sf --unix-socket /tmp/exapp.sock http://localhost/heartbeat || curl -sf "http://127.0.0.1:${APP_PORT}/heartbeat"'

ENTRYPOINT ["/sbin/tini", "--", "/start.sh", "/opt/venv/bin/python", "/app/exapp.py"]
