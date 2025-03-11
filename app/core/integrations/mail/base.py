import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.settings import settings

class BaseEmailService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.password = settings.SMTP_PASSWORD.get_secret_value()

        template_dir = settings.paths.EMAIL_TEMPLATES_DIR

        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
