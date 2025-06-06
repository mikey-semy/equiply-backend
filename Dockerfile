FROM python:3.11.11-slim as builder

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Настраиваем uv
ENV UV_HTTP_TIMEOUT=300
ENV UV_CONCURRENT_DOWNLOADS=1

# Устанавливаем зависимости
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11.11-slim

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем только runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    poppler-utils \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем виртуальное окружение из builder stage
COPY --from=builder /usr/src/app/.venv /usr/src/app/.venv

# Копируем приложение
COPY . /usr/src/app/

# Активируем виртуальное окружение
ENV PATH="/usr/src/app/.venv/bin:$PATH"

RUN chmod +x /usr/src/app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["sh", "/usr/src/app/docker-entrypoint.sh"]
