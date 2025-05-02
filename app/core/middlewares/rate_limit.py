"""Middleware для ограничения частоты запросов (rate limiting)."""

import logging
import time
from typing import Dict, Tuple, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import RateLimitExceededError


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения частоты запросов к API.

    Отслеживает количество запросов от каждого IP-адреса и блокирует
    запросы, если их количество превышает установленный лимит.
    """

    def __init__(
        self,
        app,
        limit: int = 100,  # Максимальное количество запросов
        window: int = 60,  # Временное окно в секундах
        exclude_paths: Optional[list] = None  # Пути, исключенные из ограничения
    ):
        """
        Инициализирует middleware для ограничения частоты запросов.

        Args:
            app: ASGI приложение
            limit: Максимальное количество запросов в заданном временном окне
            window: Временное окно в секундах
            exclude_paths: Список путей, которые не подлежат ограничению
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.exclude_paths = exclude_paths or []
        # Словарь для хранения информации о запросах: {ip: (счетчик, время_первого_запроса)}
        self.requests: Dict[str, Tuple[int, float]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next):
        """
        Обрабатывает запрос и применяет ограничение частоты.

        Args:
            request: Входящий HTTP-запрос
            call_next: Функция для передачи запроса следующему обработчику

        Returns:
            Response: HTTP-ответ
        """
        # Проверяем, нужно ли применять ограничение к данному пути
        path = request.url.path
        if any(path.startswith(exclude_path) for exclude_path in self.exclude_paths):
            return await call_next(request)

        # Получаем IP-адрес клиента
        client_ip = request.client.host if request.client else "unknown"

        # Текущее время
        current_time = time.time()

        # Если IP уже есть в словаре
        if client_ip in self.requests:
            count, start_time = self.requests[client_ip]

            # Если временное окно истекло, сбрасываем счетчик
            if current_time - start_time > self.window:
                self.requests[client_ip] = (1, current_time)
            else:
                # Увеличиваем счетчик
                count += 1
                self.requests[client_ip] = (count, start_time)

                # Если превышен лимит, возвращаем ошибку
                if count > self.limit:
                    self.logger.warning(
                        f"Превышен лимит запросов для IP {client_ip}",
                        extra={
                            "client_ip": client_ip,
                            "path": path,
                            "method": request.method,
                            "count": count,
                            "limit": self.limit,
                            "window": self.window
                        }
                    )

                    # Вычисляем, сколько секунд осталось до сброса ограничения
                    reset_time = int(start_time + self.window - current_time)

                    # Возвращаем ошибку 429 Too Many Requests
                    raise RateLimitExceededError(reset_time=reset_time)
        else:
            # Если это первый запрос с данного IP, добавляем его в словарь
            self.requests[client_ip] = (1, current_time)

        # Передаем запрос дальше
        response = await call_next(request)

        # Добавляем заголовки с информацией о лимитах
        if client_ip in self.requests:
            count, _ = self.requests[client_ip]
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - count))
            response.headers["X-RateLimit-Reset"] = str(int(self.window - (current_time - self.requests[client_ip][1])))

        return response
