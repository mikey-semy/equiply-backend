"""
Модуль обработчиков исключений для FastAPI.

Этот модуль содержит набор обработчиков, которые преобразуют различные типы исключений
в стандартизированный формат ответа API. Все обработчики возвращают JSON-ответ
с полями, соответствующими схеме ErrorResponseSchema.

Обработчики обеспечивают:
1. Единый формат ответов для всех типов ошибок
2. Добавление временной метки и идентификатора запроса
3. Включение информации из соответствующего исключения
4. Унификацию с полями BaseResponseSchema (success, message)

Каждый обработчик предназначен для определенного типа исключения и возвращает
соответствующий HTTP-код состояния и содержимое ответа.
"""
from typing import Any, Dict, Optional
from datetime import datetime
import uuid
import pytz

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocketDisconnect
from app.core.exceptions import AuthenticationError
from app.core.exceptions import BaseAPIException

# Московская временная зона для временных меток
moscow_tz = pytz.timezone("Europe/Moscow")

def create_error_response(
    status_code: int,
    detail: str,
    error_type: str,
    request_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    flat_structure: bool = False  # Новый параметр для выбора структуры
) -> JSONResponse:
    """
    Создает стандартизированный JSON-ответ с информацией об ошибке.

    Базовая функция для всех обработчиков исключений, обеспечивает
    единый формат ответов с ошибками.

    Args:
        status_code: HTTP код состояния
        detail: Подробное описание ошибки
        error_type: Тип ошибки для идентификации на клиенте
        request_id: Уникальный идентификатор запроса (генерируется, если не указан)
        extra: Дополнительные данные об ошибке
        flat_structure: Если True, возвращает плоскую структуру JSON для лучшей совместимости

    Returns:
        JSONResponse: HTTP-ответ со стандартизированной структурой
    """
    if request_id is None:
        request_id = str(uuid.uuid4())

    timestamp = datetime.now(moscow_tz).isoformat()

    # Для Swagger UI проверяем, если это запрос от Swagger
    headers = {}

    # Для запросов с Authorization: Bearer добавляем заголовок WWW-Authenticate
    if status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"

    # Выбор структуры ответа в зависимости от параметра flat_structure
    if flat_structure:
        # Плоская структура для лучшей совместимости со Swagger UI
        content = {
            "detail": detail,
            "error_type": error_type,
            "status_code": status_code,
            "timestamp": timestamp,
            "request_id": request_id,
            "error": extra
        }

        # Добавляем дополнительные поля из extra, если они есть
        if extra:
            for key, value in extra.items():
                content[key] = value
    else:
        # Вложенная структура для стандартного формата API
        content = {
            "success": False,
            "message": None,
            "data": None,
            "error": {
                "detail": detail,
                "error_type": error_type,
                "status_code": status_code,
                "timestamp": timestamp,
                "request_id": request_id,
                "extra": extra
            }
        }

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers
    )


async def api_exception_handler(_request: Request, exc: BaseAPIException):
    """
    Обработчик для кастомных исключений, наследующихся от BaseAPIException.

    Преобразует BaseAPIException в структурированный JSON-ответ с сохранением
    всей информации из исключения и добавлением полей для соответствия схеме ErrorResponseSchema.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (BaseAPIException): Исключение, наследующееся от BaseAPIException

    Returns:
        JSONResponse: HTTP-ответ с кодом состояния из исключения и структурированным JSON-телом
    """
    request_id = exc.extra.get("request_id", None)

    return create_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type=exc.error_type,
        request_id=request_id,
        extra=exc.extra
    )

async def http_exception_handler(_request: Request, exc: HTTPException):
    """
    Базовый обработчик стандартных HTTP-исключений.

    Преобразует HTTPException из FastAPI/Starlette в структурированный JSON-ответ
    с добавлением полей для соответствия схеме ErrorResponseSchema.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (HTTPException): Стандартное HTTP-исключение

    Returns:
        JSONResponse: HTTP-ответ с кодом состояния из исключения и структурированным JSON-телом
    """
    return create_error_response(
        status_code=exc.status_code,
        detail=str(exc.detail),
        error_type="http_error"
    )

async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации данных запроса.

    Преобразует ошибки валидации Pydantic в структурированный JSON-ответ
    с детальной информацией о каждой проблеме в данных запроса.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (RequestValidationError): Исключение валидации Pydantic

    Returns:
        JSONResponse: HTTP-ответ с кодом 422 и структурированным JSON-телом,
                     содержащим список всех ошибок валидации
    """
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Ошибка валидации данных",
        error_type="validation_error",
        extra={"errors": errors}
    )

async def websocket_exception_handler(_request: Request, exc: Exception):
    """
    Обработчик исключений WebSocket соединений.

    Обрабатывает ошибки, возникающие в WebSocket-соединениях,
    преобразуя их в стандартизированный JSON-ответ.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (Exception): Исключение, возникшее в WebSocket-обработчике

    Returns:
        JSONResponse: HTTP-ответ с кодом 500 и структурированным JSON-телом
                     с информацией об ошибке WebSocket
    """
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Ошибка WebSocket соединения",
        error_type="websocket_error",
        extra={"error": str(exc)}
    )

async def auth_exception_handler(_request: Request, exc: Exception):
    """
    Обработчик ошибок аутентификации и авторизации.

    Обрабатывает исключения, связанные с процессами аутентификации и авторизации,
    которые не наследуются от BaseAPIException.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (Exception): Исключение аутентификации/авторизации

    Returns:
        JSONResponse: HTTP-ответ с кодом 401 и структурированным JSON-телом
                     с информацией об ошибке авторизации
    """
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка авторизации",
        error_type="auth_error",
        extra={"error": str(exc)},
        flat_structure=True,
    )

async def internal_exception_handler(_request: Request, exc: Exception):
    """
    Общий обработчик непредвиденных ошибок.

    Обрабатывает все непредвиденные исключения, которые не были обработаны
    специализированными обработчиками. Предназначен для использования в качестве
    запасного варианта для обеспечения согласованного формата ответа API даже
    при возникновении неожиданных ошибок.

    Args:
        request (Request): Объект HTTP-запроса FastAPI
        exc (Exception): Любое необработанное исключение

    Returns:
        JSONResponse: HTTP-ответ с кодом 500 и структурированным JSON-телом
                     с общей информацией о внутренней ошибке сервера
    """
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Внутренняя ошибка сервера",
        error_type="internal_error",
        extra={"error": str(exc)}
    )

def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрация обработчиков исключений в FastAPI-приложении.
    Эта функция регистрирует обработчики исключений для различных типов исключений,
    которые могут возникнуть при обработке HTTP-запросов и WebSocket-соединений.

    Args:
        app (FastAPI): Экземпляр FastAPI-приложения, в котором будут регистрироваться обработчики.
    """
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(WebSocketDisconnect, websocket_exception_handler)
    app.add_exception_handler(AuthenticationError, auth_exception_handler)
    app.add_exception_handler(Exception, internal_exception_handler)