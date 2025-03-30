#!/usr/bin/bash

set -e

echo "Создаём файл логов и выставляем права"
touch /var/log/app.log 2>&1 || echo "Не удалось создать файл логов: $?"
chmod 666 /var/log/app.log 2>&1 || echo "Не удалось установить права: $?"

# echo "Создаём файл логов для Celery"
# touch /var/log/celery.log 2>&1 || echo "Не удалось создать файл логов: $?"
# chmod 666 /var/log/celery.log 2>&1 || echo "Не удалось установить права: $?"

echo "Создаём файл логов для Email Consumer"
touch /var/log/consumer.log 2>&1 || echo "Не удалось создать файл логов: $?"
chmod 666 /var/log/consumer.log 2>&1 || echo "Не удалось установить права: $?"

# echo "Запускаем Celery worker в фоновом режиме"
# celery -A app.core.integrations.worker.base worker --loglevel=info --logfile=/var/log/celery.log --detach

echo "Запускаем Email Consumer в фоновом режиме"
python -m scripts.commands start_email_consumer > /var/log/consumer.log 2>&1 &

echo "Запуск сервиса"
uv run start