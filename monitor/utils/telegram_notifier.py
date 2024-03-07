import os
import requests

TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN", None)
TELEGRAM_API_URL = "https://api.telegram.org"


def telegram_send_message(text: str, chat_id: str, disable_notification=False) -> dict:
    data = {
        "text": text,
        "chat_id": chat_id,
        "parse_mode": "markdown",
        "disable_notification": disable_notification,
    }
    try:
        r = requests.post(f"{TELEGRAM_API_URL}/bot{TELEGRAM_API_TOKEN}/sendMessage", json=data)
        return r.json()
    except Exception as err:
        print(f'[ERROR] Exception while sending Telegram message: {str(err)}')
        return {'error': str(err)}
