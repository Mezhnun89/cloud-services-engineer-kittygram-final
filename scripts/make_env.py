"""Create a private Compose env file; never print credentials."""
import os
from pathlib import Path

values = {
    'POSTGRES_DB': 'kittygram',
    'POSTGRES_USER': 'kittygram_user',
    'POSTGRES_PASSWORD': os.environ['POSTGRES_PASSWORD'],
    'SECRET_KEY': os.environ['DJANGO_SECRET_KEY'],
    'DB_HOST': 'postgres',
    'DB_PORT': '5432',
    'DEBUG': 'False',
    'ALLOWED_HOSTS': f"localhost,127.0.0.1,{os.environ['VM_IP']}",
    'DOCKERHUB_USERNAME': os.environ['DOCKERHUB_USERNAME'],
    'IMAGE_TAG': os.environ['IMAGE_TAG'],
    'GATEWAY_PORT': os.environ['GATEWAY_PORT'],
}
for name, value in values.items():
    if not value or any(char in value for char in "\r\n'\\\x00"):
        raise SystemExit(f'{name}: empty value or unsupported characters')
path = Path('.env')
with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
    for name, value in values.items():
        f.write(f"{name}='{value}'\n")
