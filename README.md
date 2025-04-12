# Equiply

## Описание проекта

**Equiply** — это современная система управления оборудованием, предназначенная для автоматизации процессов обслуживания и оптимизации работы с техническими средствами. Наша платформа помогает эффективно управлять, обслуживать и применять оборудование в различных сферах.

## Установка

Клонируйте репозиторий в директорию, в которой находитесь:
```bash
git clone https://github.com/mikey-semy/equiply-backend.git .
```
Или:
```bash
git clone https://github.com/mikey-semy/equiply-backend.git
```
Перейдите в директорию с проектом:
```bash
cd ./equiply-backend
```

> [!NOTE]
> Перед тем, как запускать проект, проверьте наличие файла `.env`

## Настройка окружения

Перед запуском проекта необходимо настроить переменные окружения.
В проекте используется файл `.env.dev` для разработки.

Скопируйте пример конфигурации из .env.example в новый файл .env.dev:
```bash
cp .env.example .env.dev
```

Отредактируйте файл .env.dev, заполнив следующие обязательные параметры:

### Основные настройки
- `ADMIN_EMAIL` - email администратора системы (с данным адресом нужно будет зарегистрировать в системе)
- `TOKEN_SECRET_KEY` - секретный ключ для JWT токенов (используйте надежный случайный ключ)
- `DOCS_USERNAME` - имя пользователя для доступа к docs (по умолчанию admin)
- `DOCS_PASSWORD` - пароль для доступа к docs (для разработки обычно admin)

### Настройки базы данных PostgreSQL
- `POSTGRES_USER` - имя пользователя PostgreSQL
- `POSTGRES_PASSWORD` - пароль пользователя PostgreSQL
- `POSTGRES_HOST` - хост базы данных (обычно localhost для разработки)
- `POSTGRES_PORT` - порт PostgreSQL (по умолчанию 5432)
- `POSTGRES_DB` - имя базы данных

### Настройки RabbitMQ
- `RABBITMQ_USER` - имя пользователя RabbitMQ (по умолчанию admin)
- `RABBITMQ_PASS` - пароль пользователя RabbitMQ (по умолчанию admin)
- `RABBITMQ_PORT` - порт RabbitMQ (по умолчанию 5672)
- `RABBITMQ_UI_PORT` - порт для UI RabbitMQ (по умолчанию 15672)
- `RABBITMQ_HOST` - хост (по умолчанию localhost)
- `RABBITMQ_EXCHANGE` - имя обмена (по умолчанию crm)

### Настройки Redis
- `REDIS_HOST` - хост Redis (обычно localhost для разработки)
- `REDIS_PORT` - порт Redis (по умолчанию 6379)
- `REDIS_PASSWORD` - пароль для Redis (обычно default для разработки)

### Настройки SMTP для отправки email (в разработке не применяется)
- `SMTP_PORT` - порт SMTP сервера (по умолчанию 587)
- `SMTP_USERNAME` - имя пользователя SMTP (по умолчанию admin)
- `SMTP_PASSWORD` - пароль SMTP (обычно admin)

### Настройки OAuth (для авторизации через внешние сервисы)
Для каждого провайдера (Yandex, VK, Google) необходимо указать:

- `client_id` - ID клиента, полученный при регистрации приложения
- `client_secret` - секретный ключ клиента
- `callback_url` - URL для обратного вызова (по умолчанию http://localhost:8000/api/v1/oauth/{provider}/callback для локальной разработки)

### Настройки S3 хранилища
- `AWS_SERVICE_NAME` - имя сервиса (по умолчанию s3)
- `AWS_REGION` - регион S3 (по умолчанию ru-central1)
- `AWS_ENDPOINT` - URL эндпоинта S3 (по умолчанию https://storage.yandexcloud.net)
- `AWS_BUCKET_NAME` - имя бакета (по умолчанию drivers.data)
- `AWS_ACCESS_KEY_ID` - ID ключа доступа ([подробнее](https://yandex.cloud/ru/docs/storage/tools/boto))
- `AWS_SECRET_ACCESS_KEY` - секретный ключ доступа ([подробнее](https://yandex.cloud/ru/docs/storage/tools/boto))

### Yandex GPT API configuration ([подробнее](https://yandex.cloud/ru/docs/foundation-models/operations/get-api-key))
- `YANDEX_API_KEY` - API ключ для доступа к Yandex GPT API
- `YANDEX_FOLDER_ID` - идентификатор каталога, в котором размещены сервисы

### Настройки CORS
- `ALLOW_ORIGINS` - список разрешенных источников (для разработки обычно ["http://localhost:3000","http://localhost:5173"])

### Пример минимальной конфигурации для локальной разработки
```bash
ADMIN_EMAIL=your_email@example.com
TOKEN_SECRET_KEY=your_secure_random_key

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=equiply_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password

ALLOW_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```
> [!IMPORTANT]
> Никогда не коммитьте файлы .env.dev или другие файлы с реальными учетными данными в репозиторий!
>
> Убедитесь, что они добавлены в .gitignore.

## Первый запуск

`PowerShell`
```bash
.\scripts\activate.ps1
```

## Последующий запуск

Для активации виртуального окружения без запуска режима разработки:

`PowerShell`
```bash
.\scripts\setup.ps1
```

Запуск в режиме разработки (с hot-reload)
```bash
uv run dev
```

Или запуск в режиме разработки (с hot-reload)   одной командой:

`PowerShell`
```bash
.\scripts\activate.ps1
```

## Разработка

### Процесс разработки такой:
- Разработка идёт от `dev`
- В dev мерджим фичи
- Тестим на `dev`
- Когда всё ок - мерджим `dev` в main

Если вы хотите внести изменения или улучшения, пожалуйста, следуйте этим шагам:

1. Переключаемся на `dev` и подтягиваем последние изменения с удалённого репозитория:
```bash
git checkout dev
git pull origin dev
```

2. От `dev` создаем свою ветку разработки и сразу на неё переключаемся:
```bash
git checkout -b feature/your-name-of-feature
```

3. Кодим и по итогу добавляем все изменения в индекс:
```bash
git add .
```

4. Создаём коммит с описанием изменений
```bash
git commit -m "feat: your-changes"
```

5. Перед пушем обновляем ветку от `dev`, то есть
 1) Переключаемся обратно на dev
 2) Подтягиваем новые изменения
 3) Возвращаемся на свою ветку
 4) Переносим свои изменения поверх последней версии `dev`

```bash
git checkout dev
git pull origin dev
git checkout feature/your-name-of-feature
git rebase dev
```

6. Отправляем свою ветку в удалённый репозиторий:
```bash
git push origin feature/your-name-of-feature --force-with-lease
```

7. Создаем Pull Request в dev ветку!
> 1) Жмём кнопку "New Pull Request"
> 2) В base выбираем `dev` (КУДА льём)
> 3) В compare выбираем свою ветку feature/your-name-of-feature (ОТКУДА льём)
> 4) Пишешь нормальное описание что сделали
> 5) Добавляем ревьюеров
> 6) Создаёи PR

Либо просто делаем merge в dev ветку из своей feature/your-name-of-feature ветки.
```bash
git checkout dev
git merge feature/your-name-of-feature
```

8. После тестирования на `dev`, создаём PR из `dev` в `main`.
> 1) Создаём новый PR
> 2) В base выбираем main (КУДА льём)
> 3) В compare выбираем dev (ОТКУДА льём)
> 4) Описываем все изменения которые войдут в прод
> 6) Ждём подтверждения от тимлида

Либо просто делаем merge в main ветку из dev ветки.
```bash
git checkout main
git merge dev
```

9. Удаляем свою ветку feature/your-name-of-feature

Локально:

```bash
git branch -d feature/your-name-of-feature
```
Удалённо:
```bash
git push origin --delete feature/your-name-of-feature
```

## Контакты
Если у вас есть вопросы или предложения, вы можете обратиться по адресу telegram: [@mikey_semi](https://t.me/mikey_semi).

Спасибо за интерес к проекту Equiply!

Мы надеемся, что эта документация поможет вам начать работу и внести свой вклад в развитие платформы.