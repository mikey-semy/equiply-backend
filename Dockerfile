FROM python:3.11.11-alpine3.19

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update

# Базовые инструменты сборки
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev

# PostgreSQL без dev пакетов (избегаем LLVM)
RUN apk add --no-cache \
    libpq-dev \
    postgresql-client

# Дополнительные утилиты
RUN apk add --no-cache poppler-utils

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 8000

COPY . /usr/src/app/

ENV UV_HTTP_TIMEOUT=60
RUN uv sync --frozen --no-cache

RUN chmod +x /usr/src/app/docker-entrypoint.sh

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
