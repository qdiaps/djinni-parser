import requests

def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            raise Exception(f'Error sending TG message: {response.text}')
    except Exception as e:
        raise Exception(f'Connection error when sending TG message: {e}')
