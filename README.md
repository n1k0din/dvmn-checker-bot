# Присылает оповещения о проверке работ на dvmn.org
- `cheker_bot.py` создает бота, слушает апи, шлёт оповещение

## Установка и настройка

Для работы необходим Python 3.9 или новее!

### Подготовка скрипта

1. Скачайте код и перейдите в папку проекта.
    ```bash
    git clone https://github.com/n1k0din/dvmn-checker-bot
    ```  
    ```bash
    cd dvmn-checker-bot
    ```
2. Установите вирт. окружение.
    ```bash
    python -m venv venv
    ```
3. Активируйте.
    ```bash
    venv\Scripts\activate.bat
    ```
    или
    ```bash
    source venv/bin/activate
    ```
4. Установите необходимые пакеты.
    ```bash
    pip install -r requirements.txt
    ```

## Подготовьте переменные окружения

Установите следующие переменные окружения (см. `.env.example`):
- `DEVMAN_API_TOKEN` - API токен Девмана получить [на Девмане](https://dvmn.org/api/docs/)
- `TELEGRAM_API_TOKEN` - Токен ТГ бота получить от [Отца ботов](https://telegram.me/BotFather)
- `NOTIFICATIONS_CHAT_ID` - ИД получателя оповещений получить от [специального бота](https://telegram.me/userinfobot) 

## Запуск

```bash
python checker_bot.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
