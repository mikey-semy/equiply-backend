# Импортируем все обработчики для их регистрации
from app.core.lifespan.base import lifespan
from app.core.lifespan.clients import initialize_clients, close_clients
from app.core.lifespan.admin import initialize_admin

# Экспортируем только lifespan для использования в main.py
__all__ = ["lifespan"]