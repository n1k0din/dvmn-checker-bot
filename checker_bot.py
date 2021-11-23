import os
import textwrap
from time import sleep
from typing import Generator, Optional

import requests
import telegram
from dotenv import load_dotenv

API_URL = 'https://dvmn.org/api'


def generate_long_polling_reviews(
    api_token: str,
    api_url: str = API_URL,
    reconnect_timeout: int = 5,
) -> Generator[dict, None, None]:
    """Gets user reviews via long polling."""
    url = f'{api_url}/long_polling'
    headers = {
        'Authorization': f'Token {api_token}',
    }
    params = {}
    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(reconnect_timeout)

        response.raise_for_status()
        reviews = response.json()
        yield reviews

        timestamp = get_timestamp(reviews)
        if timestamp:
            params['timestamp'] = timestamp


def get_timestamp(reviews: dict) -> Optional[str]:
    """Gets timestamp from response."""
    status_timestamp_mapping = {
        'found': 'last_attempt_timestamp',
        'timeout': 'timestamp_to_request',
    }
    status = reviews.get('status')
    return reviews.get(status_timestamp_mapping[status])


def build_notification(attempt: dict) -> str:
    """Build notification message in depends on attempt."""
    is_negative_message = {
        True: 'К счатью, в работе нашлись ошибки!',
        False: 'Ну, вроде ок.',
    }

    lesson_title = attempt['lesson_title']
    lesson_url = attempt['lesson_url']
    is_negative = attempt['is_negative']

    message = f'''\
        Работа "{lesson_title}" проверена.
        {is_negative_message[is_negative]}
        Ссылка на урок: {lesson_url}.
    '''
    return textwrap.dedent(message)


if __name__ == '__main__':
    load_dotenv()
    dvmn_api_token = os.getenv('DEVMAN_API_TOKEN')
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    chat_id = os.getenv('NOTIFICATIONS_CHAT_ID')
    bot = telegram.Bot(token=telegram_api_token)

    for review in generate_long_polling_reviews(dvmn_api_token):
        is_found = review.get('status') == 'found'
        if is_found:
            for attempt in review.get('new_attempts'):
                notification = build_notification(attempt)
                bot.send_message(chat_id=chat_id, text=notification)
