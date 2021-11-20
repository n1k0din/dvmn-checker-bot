import os
from typing import Generator

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

DVMN_API_TOKEN = os.getenv('DEVMAN_API_TOKEN')
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHAT_ID = os.getenv('NOTIFICATIONS_CHAT_ID')
API_URL = 'https://dvmn.org/api'


def generate_long_polling_reviews(
    api_url: str = API_URL,
    api_token: str = DVMN_API_TOKEN,
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
        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ):
            continue

        response.raise_for_status()
        reviews = response.json()
        yield reviews
        params['timestamp'] = reviews.get('timestamp_to_request')


def send_message(bot: telegram.Bot, message: str, chat_id: int = CHAT_ID):
    """Sends message from bot to chat."""
    bot.send_message(chat_id=chat_id, text=message)


def generate_review_notifications(lesson_review: dict) -> Generator[str, None, None]:
    """Generate notifications for all attempts in review response."""
    for attempt in lesson_review.get('new_attempts'):
        yield build_notification_of_attempt(attempt)


def build_notification_of_attempt(lesson_attempt: dict) -> str:
    """Build notification message in depends on attempt."""
    is_negative_message = {
        True: 'К счатью, в работе нашлись ошибки!',
        False: 'Ну, вроде ок.',
    }

    lesson_title = lesson_attempt['lesson_title']
    lesson_url = lesson_attempt['lesson_url']
    is_negative = lesson_attempt['is_negative']

    message_parts = (
        f'Работа "{lesson_title}" проверена.',
        is_negative_message[is_negative],
        f'Ссылка на урок: {lesson_url}.',
    )
    return '\n'.join(message_parts)


if __name__ == '__main__':
    bot = telegram.Bot(token=TELEGRAM_API_TOKEN)

    for review in generate_long_polling_reviews():
        is_found = review.get('status') == 'found'
        if is_found:
            for notification in generate_review_notifications(review):
                send_message(bot, notification)
