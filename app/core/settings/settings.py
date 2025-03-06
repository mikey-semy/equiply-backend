from typing import List, Dict, Any
from pydantic import SecretStr, AmqpDsn, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.lifespan import lifespan


class LoggingSettings(BaseSettings):
    """Конфигурация логирования"""
    LOG_FORMAT: str = "pretty"
    LOG_FILE: str = "app.log"
    LEVEL: str = "DEBUG"
    MAX_BYTES: int = 10485760  # 10MB
    BACKUP_COUNT: int = 5
    ENCODING: str = "utf-8"
    FILE_MODE: str = "a"
    FILE_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    PRETTY_FORMAT: str = "\033[1;36m%(asctime)s\033[0m - \033[1;32m%(name)s\033[0m - %(levelname)s - %(message)s"

    JSON_FORMAT: dict = {
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "module": "%(module)s",
        "function": "%(funcName)s",
        "message": "%(message)s"
    }

    def to_dict(self) -> dict:
        return {
            "level": self.LEVEL,
            "filename": self.LOG_FILE,
            "maxBytes": self.MAX_BYTES,
            "backupCount": self.BACKUP_COUNT,
            "encoding": self.ENCODING,
            "filemode": self.FILE_MODE,
            "format": self.PRETTY_FORMAT if self.LOG_FORMAT == "pretty" else None,
            "json_format": self.JSON_FORMAT if self.LOG_FORMAT == "json" else None,
            "force": True,
            "file_json": True
        }

class Settings(BaseSettings):
    """
    Настройки приложения

    """

    logging: LoggingSettings = LoggingSettings()

    TITLE: str = "CRM"
    DESCRIPTION: str = "CRM - это система управления взаимоотношениями с клиентами."
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def app_params(self) -> dict:
        """
        Параметры для инициализации FastAPI приложения.

        Returns:
            Dict с настройками FastAPI
        """
        return {
            "title": self.TITLE,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
            "root_path": "",
            "lifespan": lifespan,
        }

    @property
    def uvicorn_params(self) -> dict:
        """
        Параметры для запуска uvicorn сервера.

        Returns:
            Dict с настройками uvicorn
        """
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,
            "log_level": "debug",
        }

    # Настройки доступа в docs/redoc
    DOCS_ACCESS: bool = True
    DOCS_USERNAME: str = "admin"
    DOCS_PASSWORD: SecretStr = "admin"

    # Настройки логирования
    LOG_FORMAT: str = "pretty"
    LOG_FILE: str = "./logs/app.log" #if os.name == "nt" else "/var/log/app.log"
    LOG_LEVEL: str = "DEBUG"

    # Настройки Redis
    REDIS_USER: str = "default"
    REDIS_PASSWORD: SecretStr
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_POOL_SIZE: int = 10

    @property
    def redis_dsn(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            username=self.REDIS_USER,
            password=self.REDIS_PASSWORD.get_secret_value(),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=f"/{self.REDIS_DB}"
        )

    @property
    def redis_url(self) -> str:
        return str(self.redis_dsn)

    @property
    def redis_params(self) -> Dict[str, Any]:
        return {
            "url": self.redis_url,
            "pool_size": self.REDIS_POOL_SIZE
        }

    # Настройки базы данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @property
    def database_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        )

    @property
    def database_url(self) -> str:
        """
        Для alembic нужно строку с подключением к БД
        """
        return str(self.database_dsn)

    @property
    def database_params(self) -> Dict[str, Any]:
        """
        Формирует параметры подключения к БД для SQLAlchemy
        """
        return {
            "autocommit": False,
            "autoflush": False,
            "expire_on_commit": False,
            "class_": AsyncSession,
            "echo": True
        }

    # Настройки RabbitMQ
    RABBITMQ_CONNECTION_TIMEOUT: int = 30
    RABBITMQ_EXCHANGE: str = "crm"
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: SecretStr
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    @property
    def rabbitmq_dsn(self) -> AmqpDsn:
        return AmqpDsn.build(
            scheme="amqp",
            username=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD.get_secret_value(),
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT
        )

    @property
    def rabbitmq_url(self) -> str:
        """
        Для pika нужно строку с подключением к RabbitMQ
        """
        return str(self.rabbitmq_dsn)

    @property
    def rabbitmq_params(self) -> Dict[str, Any]:
        """
        Формирует параметры подключения к RabbitMQ.

        Returns:
            Dict с параметрами подключения к RabbitMQ
        """
        return {
            "url": self.rabbitmq_url,
            "connection_timeout": self.RABBITMQ_CONNECTION_TIMEOUT,
            "exchange": self.RABBITMQ_EXCHANGE,
        }

    # Настройки AWS
    AWS_SERVICE: str = "s3"
    AWS_REGION: str = "ru-central1"
    AWS_ENDPOINT: str
    AWS_BUCKET: str = "crm-bucket"
    AWS_ACCESS_KEY: SecretStr
    AWS_SECRET_KEY: SecretStr

    @property
    def s3_params(self) -> Dict[str, Any]:
        """
        Формирует информацию о конфигурации S3.
        """
        return {
            "aws_service_name": self.AWS_SERVICE,
            "aws_region": self.AWS_REGION,
            "aws_endpoint": self.AWS_ENDPOINT,
            "aws_bucket_name": self.AWS_BUCKET,
            "aws_access_key_id": self.AWS_ACCESS_KEY,
            "aws_secret_access_key": self.AWS_SECRET_KEY,
        }

    # Настройки CORS
    ALLOW_ORIGINS: List[str] = []
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    @property
    def cors_params(self) -> Dict[str, Any]:
        """
        Формирует параметры CORS для FastAPI.

        Returns:
            Dict с настройками CORS middleware
        """
        return {
            "allow_origins": self.ALLOW_ORIGINS,
            "allow_credentials": self.ALLOW_CREDENTIALS,
            "allow_methods": self.ALLOW_METHODS,
            "allow_headers": self.ALLOW_HEADERS,
        }

    model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            env_nested_delimiter="__",
            extra="allow"
        )