FROM python:3.11.11-alpine3.19 as builder

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем все build dependencies одной командой
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Копируем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Увеличиваем таймауты и настраиваем uv
ENV UV_HTTP_TIMEOUT=300
ENV UV_CONCURRENT_DOWNLOADS=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11.11-alpine3.19

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем только runtime dependencies
RUN apk update && apk add --no-cache \
    postgresql-client \
    poppler-utils \
    libpq \
    && rm -rf /var/cache/apk/*

# Копируем виртуальное окружение из builder stage
COPY --from=builder /usr/src/app/.venv /usr/src/app/.venv

# Копируем приложение
COPY . /usr/src/app/

# Активируем виртуальное окружение
ENV PATH="/usr/src/app/.venv/bin:$PATH"

RUN chmod +x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]