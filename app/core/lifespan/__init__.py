# Импортируем все обработчики для их регистрации
from app.core.lifespan.access import initialize_default_policies
from app.core.lifespan.admin import initialize_admin
from app.core.lifespan.base import lifespan
from app.core.lifespan.clients import close_clients, initialize_clients
# Экспортируем только lifespan для использования в main.py
__all__ = ["lifespan"]
