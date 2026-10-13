"""Contrôles du conditionnement de l'ExApp : manifeste AppAPI, version du moteur, script HaRP, paquet de la boutique.
Le contrat lui-même (cycle de vie, en-têtes, rôles, droits) est testé dans le dépôt du moteur (tests/test_v5642.py, classe ExApp) ;
si ``AXIORHUB_ENGINE`` désigne une copie du moteur, la passerelle est aussi vérifiée ici."""
import base64
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Manifest(unittest.TestCase):
    def setUp(self):
        self.info = ET.parse(ROOT / 'appinfo' / 'info.xml').getroot()

    def test_identity_versions_and_image(self):
        self.assertEqual(self.info.findtext('id'), 'axiorhub')
        version = self.info.findtext('version')
        self.assertEqual(version, self.info.findtext('external-app/docker-install/image-tag'))       # version = image-tag
        self.assertEqual(self.info.findtext('external-app/docker-install/registry'), 'ghcr.io')
        self.assertEqual(self.info.findtext('external-app/docker-install/image'), 'arthur-llevelys/axiorhub-exapp')
        nc = self.info.find('dependencies/nextcloud')
        self.assertEqual((nc.get('min-version'), nc.get('max-version')), ('32', '35'))
        self.assertTrue(all(len(s.text) <= 128 for s in self.info.findall('summary')))
        changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
        self.assertIn('## %s' % version, changelog)

    def test_routes_and_environment(self):
        routes = self.info.findall('external-app/routes/route')
        levels = [(r.findtext('url'), r.findtext('access_level')) for r in routes]
        self.assertEqual(levels[0], ('^/img/.*', 'PUBLIC'))                                         # seule l'icône est publique
        self.assertIn(('.*', 'USER'), levels)
        for r in routes:
            self.assertEqual(json.loads(r.findtext('headers_to_exclude')), ['Cookie'])
        variables = {v.findtext('name'): v for v in self.info.findall('external-app/environment-variables/variable')}
        for name in ('AXIORHUB_SERVICE_USER', 'AXIORHUB_NEXTCLOUD_ROOT', 'AXIORHUB_OLLAMA_URL', 'AXIORHUB_GROUP_AVOCATS',
                     'AXIORHUB_GROUP_COLLABORATEURS', 'AXIORHUB_GROUP_ASSISTANTS'):
            self.assertIn(name, variables)
            default = variables[name].find('default')
            self.assertTrue(default is not None and (default.text or '').strip(), name)              # jamais de <default/> vide

    def test_dockerfile_engine_and_harp(self):
        docker = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
        engine = (ROOT / 'ENGINE_VERSION').read_text(encoding='utf-8').strip()
        self.assertIn('ARG AXIORHUB_VERSION=%s' % engine, docker)
        self.assertIn('FROM alpine:3.21', docker)
        self.assertIn(' frp ', docker)
        self.assertIn('/start.sh', docker)
        self.assertIn('/app/exapp.py', docker)
        self.assertIn('HEALTHCHECK', docker)
        start = (ROOT / 'start.sh').read_text(encoding='utf-8')
        for mark in ('HP_SHARED_KEY', 'unixPath = "/tmp/exapp.sock"', 'frpc -c /frpc.toml &', 'exec "$@"'):
            self.assertIn(mark, start)

    def test_appstore_package_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            outs = []
            for n in (1, 2):
                target = Path(tmp) / ('a%d.tar.gz' % n)
                subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build-appstore-package.py'), str(target)], check=True,
                               stdout=subprocess.DEVNULL)
                outs.append(target.read_bytes())
            self.assertEqual(outs[0], outs[1])
            with tarfile.open(fileobj=io.BytesIO(outs[0])) as tar:
                names = sorted(tar.getnames())
            self.assertIn('axiorhub/appinfo/info.xml', names)
            self.assertTrue(all(n.startswith('axiorhub/') for n in names))


@unittest.skipUnless(os.environ.get('AXIORHUB_ENGINE'), 'copie du moteur non fournie (AXIORHUB_ENGINE)')
class EngineContract(unittest.TestCase):
    """Passerelle du moteur indiqué dans ENGINE_VERSION : battement, en-têtes AppAPI, rôle par groupe."""

    def test_gateway(self):
        sys.path.insert(0, os.environ['AXIORHUB_ENGINE'])
        from agent import exapp5642 as x
        s = x.settings({'APP_ID': 'axiorhub', 'APP_VERSION': '0.1.0', 'APP_SECRET': 'k' * 40, 'NEXTCLOUD_URL': 'https://cloud.example.test'})

        class Groups:
            def groups(self, user):
                return ['axiorhub-avocats'] if user == 'alice' else []

        seen = []
        gw = x.Gateway(lambda env, start: seen.append(env) or start('200 OK', []) or [b''], s, 't' * 40, ocs=Groups())

        def call(path, user=None):
            env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': path, 'QUERY_STRING': '', 'wsgi.input': io.BytesIO(b'')}
            if user is not None:
                env.update(HTTP_EX_APP_ID='axiorhub', HTTP_AUTHORIZATION_APP_API=base64.b64encode(('%s:%s' % (user, 'k' * 40)).encode()).decode())
            out = {}
            b''.join(gw(env, lambda status, headers, exc=None: out.update(status=status)))
            return out['status']
        self.assertTrue(call('/heartbeat').startswith('200'))
        self.assertTrue(call('/aujourdhui').startswith('403'))
        self.assertTrue(call('/aujourdhui', 'alice').startswith('200'))
        self.assertEqual(seen[-1]['HTTP_X_AXIORHUB_ROLE'], 'avocat')
        self.assertTrue(call('/aujourdhui', 'bob').startswith('403'))


class Privacy(unittest.TestCase):
    def test_privacy_scan(self):
        out = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'privacy-scan.py')], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertNotRegex((ROOT / 'appinfo' / 'info.xml').read_text(encoding='utf-8'), re.compile('raw\\.githubusercontent'))


if __name__ == '__main__':
    unittest.main()
