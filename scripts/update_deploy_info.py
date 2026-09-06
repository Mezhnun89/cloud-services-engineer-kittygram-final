"""Update the reviewer URL using the address created by Terraform."""
import ipaddress
from pathlib import Path
import sys
from urllib.parse import urlparse

import yaml

url = sys.argv[1]
parsed = urlparse(url)
ipaddress.IPv4Address(parsed.hostname)
if (parsed.scheme != 'http' or parsed.port is None
        or parsed.path or parsed.query or parsed.fragment or parsed.username):
    raise SystemExit('Expected http://IPv4:port from terraform output app_url')
path = Path(__file__).resolve().parents[1] / 'tests.yml'
data = yaml.safe_load(path.read_text())
data['kittygram_domain'] = url
path.write_text(yaml.safe_dump(data, sort_keys=False))
