# Документация по настройкам приложения

Этот документ описывает настройки конфигурации для приложения Equiply.

## Содержание
- [Документация по настройкам приложения](#документация-по-настройкам-приложения)
  - [Содержание](#содержание)
  - [Обзор](#обзор)
  - [Настройки окружения](#настройки-окружения)
  - [Настройки приложения](#настройки-приложения)
  - [Настройки аутентификации](#настройки-аутентификации)
  - [Настройки OAuth](#настройки-oauth)
  - [Настройки электронной почты](#настройки-электронной-почты)
  - [Доступ к документации](#доступ-к-документации)
  - [Настройки Redis](#настройки-redis)
  - [Настройки базы данных](#настройки-базы-данных)
  - [Настройки RabbitMQ](#настройки-rabbitmq)
  - [Настройки AWS S3](#настройки-aws-s3)
  - [Настройки Yandex GPT](#настройки-yandex-gpt)
  - [Настройки CORS](#настройки-cors)
  - [Загрузка конфигурации](#загрузка-конфигурации)

## Обзор
Приложение использует BaseSettings Pydantic для управления конфигурацией, что позволяет загружать настройки из переменных окружения, файлов `.env` и значений по умолчанию.

## Настройки окружения
Приложение определяет свое окружение и автоматически загружает соответствующий файл конфигурации:

```python
env_file_path, app_env = PathSettings.get_env_file_and_type()
```

## Настройки приложения
Основная информация о приложении и конфигурация сервера:

| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `app_env` | Окружение приложения (development, production и т.д.) | Определяется автоматически |
| `TITLE` | Название приложения | "Equiply" |
| `DESCRIPTION` | Описание приложения | "Equiply — это современная система управления оборудованием..." |
| `VERSION` | Версия API | "0.1.0" |
| `HOST` | Хост сервера | "0.0.0.0" |
| `PORT` | Порт сервера | 8000 |

Параметры приложения:
- `app_params`: Конфигурация для инициализации FastAPI (заголовок, описание, версия, Swagger UI и обработчики жизненного цикла приложения).
- `uvicorn_params`: Конфигурация для Uvicorn сервера (хост, порт, обработка прокси-заголовков, уровень логирования).

## Настройки аутентификации
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `AUTH_URL` | Конечная точка аутентификации | "api/v1/auth" |
| `TOKEN_TYPE` | Тип токена аутентификации | "Bearer" |
| `TOKEN_EXPIRE_MINUTES` | Время истечения токена в минутах | 1440 (24 часа) |
| `VERIFICATION_TOKEN_EXPIRE_MINUTES` | Время истечения токена верификации | 1440 (24 часа) |
| `TOKEN_ALGORITHM` | Алгоритм JWT | "HS256" |
| `TOKEN_SECRET_KEY` | Секретный ключ для кодирования/декодирования JWT | Обязательно |
| `USER_INACTIVE_TIMEOUT` | Время бездействия пользователя в секундах

## Настройки OAuth
Конфигурация для провайдеров OAuth (Yandex, VK, Google):

| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `OAUTH_SUCCESS_REDIRECT_URI` | URI перенаправления после успешного OAuth | "https://equiply.ru" |
| `OAUTH_CALLBACK_BASE_URL` | Базовый URL для обратных вызовов OAuth | "api/v1/oauth/{provider}/callback" |
| `OAUTH_PROVIDERS` | Словарь с конфигурациями для каждого провайдера | Настроен для Yandex, VK, Google |

Каждая конфигурация провайдера включает:
- `client_id`
- `client_secret`
- `auth_url`
- `token_url`
- `user_info_url`
- `scope`
- `callback_url`

## Настройки электронной почты
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `VERIFICATION_URL` | URL для верификации email | "https://api.equiply.ru/api/v1/register/verify-email/" |
| `PASSWORD_RESET_URL` | URL для сброса пароля | "https://api.equiply.ru/api/v1/auth/reset-password/" |
| `LOGIN_URL` | URL для входа | "https://api.equiply.ru/api/v1/auth" |
| `SMTP_SERVER` | Адрес SMTP-сервера | "smtp.gmail.com" |
| `SMTP_PORT` | Порт SMTP-сервера | 587 |
| `SENDER_EMAIL` | Адрес отправителя email | "toshkin.mikhail@gmail.com" |
| `SMTP_USERNAME` | Имя пользователя SMTP | "toshkin.mikhail@gmail.com" |
| `SMTP_PASSWORD` | Пароль SMTP | Обязательно |

## Доступ к документации
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `DOCS_ACCESS` | Включить/выключить доступ к документации API | True |
| `DOCS_USERNAME` | Имя пользователя для доступа к документации | "admin" |
| `DOCS_PASSWORD` | Пароль для доступа к документации | Обязательно |

## Настройки Redis
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `REDIS_USER` | Имя пользователя Redis | "default" |
| `REDIS_PASSWORD` | Пароль Redis | Обязательно |
| `REDIS_HOST` | Хост Redis | "localhost" |
| `REDIS_PORT` | Порт Redis | 6379 |
| `REDIS_DB` | Номер базы данных Redis | 0 |
| `REDIS_POOL_SIZE` | Размер пула подключений Redis | 10 |

Свойства подключения Redis:
- `redis_dsn`: Формирует DSN (Data Source Name) для Redis
- `redis_url`: Строковое представление DSN Redis
- `redis_params`: Словарь с параметрами подключения к Redis

## Настройки базы данных
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `POSTGRES_USER` | Имя пользователя PostgreSQL | Обязательно |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | Обязательно |
| `POSTGRES_HOST` | Хост PostgreSQL | "localhost" |
| `POSTGRES_PORT` | Порт PostgreSQL | 5432 |
| `POSTGRES_DB` | Имя базы данных PostgreSQL | Обязательно |

Свойства подключения к базе данных:
- `database_dsn`: Формирует DSN для PostgreSQL с использованием драйвера asyncpg
- `database_url`: Строковое представление DSN базы данных (для Alembic)
- `engine_params`: Конфигурация SQLAlchemy engine
- `session_params`: Конфигурация SQLAlchemy session

## Настройки RabbitMQ
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `RABBITMQ_CONNECTION_TIMEOUT` | Время ожидания подключения в секундах | 30 |
| `RABBITMQ_EXCHANGE` | Имя обмена RabbitMQ | "crm" |
| `RABBITMQ_USER` | Имя пользователя RabbitMQ | Обязательно |
| `RABBITMQ_PASS` | Пароль RabbitMQ | Обязательно |
| `RABBITMQ_HOST` | Хост RabbitMQ | "localhost" |
| `RABBITMQ_PORT` | Порт RabbitMQ | 5672 |

Свойства подключения к RabbitMQ:
- `rabbitmq_dsn`: Формирует DSN для RabbitMQ
- `rabbitmq_url`: Строковое представление DSN RabbitMQ
- `rabbitmq_params`: Словарь с параметрами подключения к RabbitMQ

## Настройки AWS S3
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `AWS_SERVICE_NAME` | Имя сервиса AWS | "s3" |
| `AWS_REGION` | Регион AWS | "ru-central1" |
| `AWS_ENDPOINT` | URL эндпоинта AWS | Обязательно |
| `AWS_BUCKET_NAME` | Имя S3 бакета | "crm-bucket" |
| `AWS_ACCESS_KEY_ID` | ID ключа доступа AWS | Обязательно |
| `AWS_SECRET_ACCESS_KEY` | Секретный ключ доступа AWS | Обязательно |

Свойство подключения к S3:
- `s3_params`: Словарь с параметрами конфигурации S3

## Настройки Yandex GPT
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `YANDEX_PRE_INSTRUCTIONS` | Предварительные инструкции для модели | "Ты ассистент, помогающий пользователю." |
| `YANDEX_TEMPERATURE` | Параметр температуры модели | 0.6 |
| `YANDEX_MAX_TOKENS` | Максимальное количество токенов в ответе | 2000 |
| `YANDEX_MODEL_NAME` | Имя модели | "llama" |
| `YANDEX_MODEL_VERSION` | Версия модели | "rc" |
| `YANDEX_API_URL` | URL API Yandex | "https://llm.api.cloud.yandex.net/foundationModels/v1/completion" |
| `YANDEX_API_KEY` | API-ключ Yandex | Обязательно |
| `YANDEX_FOLDER_ID` | ID папки Yandex | Обязательно |

Свойство Yandex GPT:
- `yandex_model_uri`: Формирует URI модели в формате `gpt://{folder_id}/{model_name}/{model_version}`

## Настройки CORS
| Настройка | Описание | Значение по умолчанию |
| --- | --- | --- |
| `ALLOW_ORIGINS` | Список разрешенных источников | [] |
| `ALLOW_CREDENTIALS` | Разрешить учетные данные | True |
| `ALLOW_METHODS` | Разрешенные HTTP-методы | ["*"] |
| `ALLOW_HEADERS` | Разрешенные HTTP-заголовки | ["*"] |

Свойство CORS:
- `cors_params`: Словарь с конфигурацией промежуточного ПО CORS

## Загрузка конфигурации
Приложение использует `SettingsConfigDict` Pydantic для загрузки конфигурации со следующими параметрами:

- Путь к файлу окружения определяется автоматически
- Кодировка файлов окружения - UTF-8
- Вложенные настройки с разделителем `__`
- Разрешены дополнительные поля