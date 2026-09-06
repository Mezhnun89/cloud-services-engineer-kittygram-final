#!/usr/bin/env bash
set -euo pipefail
cd /home/deploy/kittygram
chmod 600 .env
compose=(sudo docker compose --env-file .env -f docker-compose.production.yml)
"${compose[@]}" pull
"${compose[@]}" up -d --wait --wait-timeout 180 postgres
"${compose[@]}" run --rm --no-deps backend python manage.py migrate --noinput
"${compose[@]}" up --no-deps --force-recreate --abort-on-container-exit --exit-code-from frontend frontend
"${compose[@]}" run --rm --no-deps backend python manage.py collectstatic --noinput
"${compose[@]}" up -d --no-deps --force-recreate backend gateway
"${compose[@]}" ps
