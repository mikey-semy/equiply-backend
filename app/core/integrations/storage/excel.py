from typing import Optional, Tuple

import pandas as pd
from botocore.client import BaseClient  # type: ignore
from fastapi import UploadFile
from io import BytesIO

from app.core.integrations.storage.base import BaseS3Storage


class ExcelS3DataManager(BaseS3Storage):
    """
    Менеджер для работы с Excel-файлами в S3 хранилище.
    Расширяет базовый класс для специфических нужд работы с Excel.
    """

    def __init__(self, s3_client: BaseClient):
        super().__init__(s3_client)
        self.excel_folder = "excel"  # Папка для хранения Excel-файлов

    async def upload_excel(
        self,
        file: UploadFile,
        file_content: Optional[bytes] = None,
        folder: str = None,
    ) -> str:
        """
        Загрузка Excel-файла в хранилище

        Args:
            file (UploadFile): Файл Excel
            file_content (Optional[bytes], optional): Байтовое представление файла. Defaults to None.
            folder (str, optional): Подпапка для хранения. Defaults to None.

        Returns:
            str: URL загруженного файла
        """
        file_key = f"{self.excel_folder}/{folder or ''}"

        try:
            result = await self.upload_file_from_content(
                file=file, file_content=file_content, file_key=file_key
            )
            self.logger.info("Загружен Excel-файл: %s", result)
            return result
        except Exception as e:
            self.logger.error("Ошибка загрузки Excel-файла: %s", str(e))
            raise ValueError(f"Не удалось загрузить Excel-файл: {str(e)}")

    async def read_excel_from_url(self, file_url: str) -> pd.DataFrame:
        """
        Чтение Excel-файла из хранилища по URL

        Args:
            file_url (str): URL файла в хранилище

        Returns:
            pd.DataFrame: DataFrame с данными из Excel
        """
        try:
            # Извлекаем ключ файла из URL
            parts = file_url.split(f"{self.endpoint}/{self.bucket_name}/")
            if len(parts) <= 1:
                raise ValueError(f"Некорректный URL файла: {file_url}")

            file_key = parts[1]

            # Создаем временный буфер для скачивания файла
            buffer = BytesIO()

            # Скачиваем файл в буфер
            await self._client.download_fileobj(
                Bucket=self.bucket_name,
                Key=file_key,
                Fileobj=buffer
            )

            # Перемещаем указатель в начало буфера
            buffer.seek(0)

            # Читаем Excel-файл
            df = pd.read_excel(buffer)

            return df
        except Exception as e:
            self.logger.error("Ошибка чтения Excel-файла: %s", str(e))
            raise ValueError(f"Не удалось прочитать Excel-файл: {str(e)}")

    async def create_excel_file(
        self,
        data: pd.DataFrame,
        filename: str,
        folder: str = None
    ) -> Tuple[str, bytes]:
        """
        Создание Excel-файла из DataFrame и загрузка в хранилище

        Args:
            data (pd.DataFrame): DataFrame с данными
            filename (str): Имя файла
            folder (str, optional): Подпапка для хранения. Defaults to None.

        Returns:
            Tuple[str, bytes]: URL файла и его содержимое в байтах
        """
        try:
            # Создаем Excel-файл в памяти
            buffer = BytesIO()
            data.to_excel(buffer, index=False)
            buffer.seek(0)
            file_content = buffer.getvalue()

            # Формируем имя файла
            if not filename.lower().endswith(('.xlsx', '.xls')):
                filename = f"{filename}.xlsx"

            # Создаем объект UploadFile
            file = UploadFile(
                filename=filename,
                file=BytesIO(file_content),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Загружаем файл в хранилище
            file_key = f"{self.excel_folder}/{folder or ''}"
            file_url = await self.upload_file_from_content(
                file=file,
                file_content=file_content,
                file_key=file_key
            )

            return file_url, file_content
        except Exception as e:
            self.logger.error("Ошибка создания Excel-файла: %s", str(e))
            raise ValueError(f"Не удалось создать Excel-файл: {str(e)}")

    async def process_excel_import(
        self,
        file: UploadFile,
        file_content: Optional[bytes] = None,
        folder: str = "imports"
    ) -> Tuple[pd.DataFrame, str]:
        """
        Обработка импорта Excel-файла: загрузка в хранилище и чтение данных

        Args:
            file (UploadFile): Файл Excel
            file_content (Optional[bytes], optional): Байтовое представление файла. Defaults to None.
            folder (str, optional): Подпапка для хранения. Defaults to "imports".

        Returns:
            Tuple[pd.DataFrame, str]: DataFrame с данными и URL файла
        """
        # Проверяем, что файл имеет расширение .xlsx или .xls
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise ValueError("Файл должен быть в формате Excel (.xlsx или .xls)")

        # Если содержимое файла не передано, читаем его
        if file_content is None:
            file_content = await file.read()

        # Загружаем файл в хранилище
        file_url = await self.upload_excel(
            file=file,
            file_content=file_content,
            folder=folder
        )

        # Читаем данные из файла
        try:
            df = pd.read_excel(BytesIO(file_content))
            return df, file_url
        except Exception as e:
            self.logger.error("Ошибка чтения данных из Excel-файла: %s", str(e))
            raise ValueError(f"Не удалось прочитать данные из Excel-файла: {str(e)}")

    async def process_excel_export(
        self,
        data: pd.DataFrame,
        filename: str,
        folder: str = "exports"
    ) -> Tuple[bytes, str]:
        """
        Обработка экспорта данных в Excel: создание файла и загрузка в хранилище

        Args:
            data (pd.DataFrame): DataFrame с данными
            filename (str): Имя файла
            folder (str, optional): Подпапка для хранения. Defaults to "exports".

        Returns:
            Tuple[bytes, str]: Содержимое файла в байтах и URL файла
        """
        # Создаем Excel-файл и загружаем в хранилище
        file_url, file_content = await self.create_excel_file(
            data=data,
            filename=filename,
            folder=folder
        )

        return file_content, file_url
