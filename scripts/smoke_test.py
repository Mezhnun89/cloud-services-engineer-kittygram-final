"""Read-only checks of the real gateway, React assets and API authentication."""
from html.parser import HTMLParser
import sys
from urllib.parse import urljoin

import requests


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs['src'])


base = sys.argv[1].rstrip('/') + '/'
response = requests.get(base, timeout=30)
response.raise_for_status()
assert '<div id="root">' in response.text, 'React root missing'
assets = Assets()
assets.feed(response.text)
assert assets.scripts, 'No React JavaScript bundle found'
for src in assets.scripts:
    asset = requests.get(urljoin(base, src), timeout=30)
    asset.raise_for_status()
    assert 'html' not in asset.headers.get('Content-Type', ''), 'SPA fallback returned instead of JS'
api = requests.get(urljoin(base, 'api/cats/'), timeout=30)
assert api.status_code == 401, f'Anonymous cats request: {api.status_code}'
assert 'application/json' in api.headers.get('Content-Type', ''), 'API returned non-JSON'
print('SMOKE_OK: React, JavaScript assets, API authentication')
