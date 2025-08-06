**Используется при инициализации и разработке:**
- `uv run setup` - настройка окружения (вызывает scripts/setup.ps1 или .sh) - если уже был первый запуск и в инициализации и установки пакетов нет необходимости, пропускает настройку окружения, просто активирует
- `uv run activate` - активация окружения (uv run setup) + запуск dev режима (uv run dev(вызывает scripts/activate.ps1 или .sh)

> [!warning]
> Команды выше не будут полноценно работать на linux/mac, пока используем нужный формат скриптов или исправляем (внутри скриптов все еще используется ps1 для windows):

```bash
./scripts/setup.sh
```

```bash
./scripts/activate.sh
```

- `uv run dev` - запуск в режиме разработки (инфраструктура + hot-reload сервер)

**Используется для проверки кода (для запуска в pre-commit):**
- `uv run check` - проверка кода (mypy + flake8 с группировкой ошибок по типам)
- `uv run format` - форматирование кода (black + isort)
- `uv run lint` - линтинг (format + check)
- `uv run test` - запуск тестов pytest с ENV_FILE=".env.test"

**Используется для работы с миграциями (не хватает ревизии и отката):**
- `uv run migrate` - запуск миграций Alembic (upgrade head)

**Используется на проде:**
- `uv run start` - запуск миграций + production сервер
- `uv run serve` - запуск production сервера uvicorn на порту 8000