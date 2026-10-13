#!/usr/bin/env python3
"""Paquet de la boutique Nextcloud pour l'ExApp : un seul dossier ``axiorhub`` avec ``appinfo/info.xml``, l'icône, la licence et la
documentation (l'image Docker est publiée séparément sur ghcr.io). Archive reproductible (dates et droits fixes).

  python3 scripts/build-appstore-package.py dist/axiorhub-0.1.0.tar.gz
"""
import gzip
import hashlib
import io
from pathlib import Path
import re
import sys
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FILES = ('appinfo/info.xml', 'img/app.svg', 'LICENSE', 'README.md', 'README.en.md', 'CHANGELOG.md')


def check_manifest():
    info = ET.parse(ROOT / 'appinfo' / 'info.xml').getroot()
    version = info.findtext('version')
    tag = info.findtext('external-app/docker-install/image-tag')
    if info.findtext('id') != 'axiorhub' or version != tag:
        raise SystemExit('info.xml : identifiant attendu « axiorhub » et version égale à image-tag (%s / %s)' % (version, tag))
    engine = (ROOT / 'ENGINE_VERSION').read_text(encoding='utf-8').strip()
    docker = re.search(r'ARG AXIORHUB_VERSION=(\S+)', (ROOT / 'Dockerfile').read_text(encoding='utf-8'))
    if not docker or docker.group(1) != engine:
        raise SystemExit('Dockerfile : AXIORHUB_VERSION différente de ENGINE_VERSION (%s)' % engine)
    return version


def build(target):
    version = check_manifest()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for rel in FILES:
            data = (ROOT / rel).read_bytes()
            info = tarfile.TarInfo('axiorhub/' + rel)
            info.size, info.mtime, info.mode, info.uid, info.gid, info.uname, info.gname = len(data), 0, 0o644, 0, 0, '', ''
            tar.addfile(info, io.BytesIO(data))
    out = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=out, mtime=0) as gz:
        gz.write(raw.getvalue())
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(out.getvalue())
    digest = hashlib.sha256(out.getvalue()).hexdigest()
    target.with_name(target.name + '.sha256').write_text('%s  %s\n' % (digest, target.name), encoding='utf-8')
    print('axiorhub %s : %s (%d fichiers) sha256 %s' % (version, target, len(FILES), digest))


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'dist/axiorhub.tar.gz')
