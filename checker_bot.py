import logging
import os
import textwrap
from time import sleep
from typing import Generator, Optional

import requests
import telegram
from dotenv import load_dotenv

logger = logging.getLogger(__file__)

API_URL = 'https://dvmn.org/api'


class TelegramLogsHandler(logging.Handler):
    """Handler for sending messages via telegram bot."""

    def __init__(self, tg_bot, chat_id):
        """Inits bot and chat id."""
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        """Sends logger message to bot."""
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


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
    logger.setLevel(logging.INFO)
    load_dotenv()
    dvmn_api_token = os.getenv('DEVMAN_API_TOKEN')
    telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
    chat_id = os.getenv('NOTIFICATIONS_CHAT_ID')
    bot = telegram.Bot(token=telegram_api_token)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info('Bot started!')

    while True:
        try:
            for review in generate_long_polling_reviews(dvmn_api_token):
                logging.info(f'Got review: {review}')
                is_found = review.get('status') == 'found'
                if is_found:
                    for attempt in review.get('new_attempts'):
                        notification = build_notification(attempt)
                        bot.send_message(chat_id=chat_id, text=notification)
                        logger.debug(f'Sent notification to {chat_id}')
        except Exception:
            logger.exception('А у бота ошибка!')
