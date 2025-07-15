"""
Модуль для управления отправкой электронной почты через SMTP протокол.

Предоставляет функциональность для отправки HTML-писем с использованием настроек 
из конфигурации приложения и поддержкой шаблонизации через Jinja2.

Зависимости:
    - logging: для ведения логов операций
    - smtplib: для работы с SMTP протоколом
    - ssl: для настройки SSL/TLS соединения
    - email.mime.text: для создания MIME сообщений
    - jinja2: для работы с email шаблонами
    - app.core.settings: для получения конфигурации приложения
"""
import logging
import smtplib
import ssl
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from app.core.settings import settings


class BaseEmailDataManager:
    """
    Базовый класс для управления отправкой электронной почты.
    
    Инкапсулирует логику подключения к SMTP серверу, аутентификации и отправки сообщений.
    Автоматически загружает SMTP настройки из конфигурации приложения и настраивает
    Jinja2 окружение для работы с email шаблонами.
    
    Attributes:
        logger: Логгер для записи операций класса
        smtp_server: Адрес SMTP сервера из настроек
        smtp_port: Порт SMTP сервера из настроек
        sender_email: Email адрес отправителя из настроек
        smtp_username: Имя пользователя для аутентификации на SMTP сервере
        smtp_password: Пароль для аутентификации (извлекается как секретное значение)
        env: Окружение Jinja2 для работы с email шаблонами
    """
    def __init__(self):
        """
        Инициализирует менеджер email с настройками из конфигурации.
        
        Загружает все необходимые SMTP настройки и настраивает Jinja2 окружение
        для работы с шаблонами из директории EMAIL_TEMPLATES_DIR.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD.get_secret_value()

        template_dir = settings.paths.EMAIL_TEMPLATES_DIR

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    async def send_email(self, to_email: str, subject: str, body: str):
        """
        Отправляет HTML электронное письмо через SMTP протокол.
        
        Выполняет полный цикл отправки: создание MIME сообщения, установка SSL соединения,
        аутентификация на SMTP сервере и отправка письма с проверкой результата.
        Включает подробное логирование всех этапов и обработку различных типов ошибок.
        
        Args:
            to_email (str): Email адрес получателя письма
            subject (str): Тема/заголовок письма
            body (str): HTML-содержимое письма (поддерживается HTML разметка)
            
        Returns:
            bool: True при успешной отправке письма всем получателям,
                  False если отправка не удалась некоторым получателям
                  
        Raises:
            SMTPConnectError: При ошибке подключения к SMTP серверу
            SMTPAuthenticationError: При ошибке аутентификации на SMTP сервере
            SMTPException: При общих ошибках SMTP протокола
            TimeoutError: При превышении времени ожидания подключения (30 секунд)
            Exception: При любых других непредвиденных ошибках
            
        Note:
            - Использует SSL/TLS шифрование с отключенной проверкой сертификата
            - Таймаут подключения установлен в 30 секунд
            - Автоматическое закрытие SMTP соединения через context manager
        """
        self.logger.info(
            "Отправка email", extra={"to_email": to_email, "subject": subject}
        )
        try:
            msg = MIMEText(body, "html")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email

            # Создаем SSL контекст и отключаем проверку сертификата
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                self.logger.debug(
                    "Подключение к SMTP серверу %s:%s", self.smtp_server, self.smtp_port
                )
                # Включаем шифрование
                server.starttls(context=context)

                # Логинимся
                server.login(self.smtp_username, self.smtp_password)

                # Отправляем сообщение и ждем ответа
                response = server.send_message(msg)

                # Проверяем, что сообщение было отправлено всем получателям
                if response:
                    failed_recipients = list(response.keys())
                    self.logger.error(
                        "Не удалось отправить email некоторым получателям: %s",
                        failed_recipients,
                        extra={"to_email": to_email, "subject": subject},
                    )
                    return False

            self.logger.info(
                "Email успешно отправлен",
                extra={"to_email": to_email, "subject": subject},
            )
            return True

        except smtplib.SMTPConnectError as e:
            self.logger.error(
                "Ошибка подключения к SMTP серверу: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(
                "Ошибка аутентификации на SMTP сервере: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except smtplib.SMTPException as e:
            self.logger.error(
                "Ошибка SMTP при отправке email: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except TimeoutError as e:
            self.logger.error(
                "Таймаут при подключении к SMTP серверу: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
        except Exception as e:
            self.logger.error(
                "Неизвестная ошибка при отправке email: %s",
                str(e),
                extra={"to_email": to_email, "subject": subject},
            )
            raise
