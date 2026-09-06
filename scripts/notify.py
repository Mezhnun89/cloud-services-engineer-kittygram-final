"""Notify the configured course Telegram chat only after successful verification."""
import os
import requests

for name in ('TELEGRAM_TO', 'TELEGRAM_TOKEN'):
    if not os.environ.get(name):
        raise SystemExit(f'Set {name} repository secret for the required notification')
try:
    result = requests.post(
        'https://api.telegram.org/bot' + os.environ['TELEGRAM_TOKEN'] + '/sendMessage',
        json={
            'chat_id': os.environ['TELEGRAM_TO'],
            'text': f"Kittygram: деплой и проверки пройдены. {os.environ['APP_URL']} "
                    f"Коммит: {os.environ['GITHUB_SHA']}",
        }, timeout=30,
    )
    if result.status_code != 200 or not result.json().get('ok'):
        raise SystemExit('Telegram notification failed; check bot access and chat ID')
except requests.RequestException:
    raise SystemExit('Telegram request failed (credentials omitted)') from None
