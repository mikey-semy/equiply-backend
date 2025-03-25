from typing import Optional

from botocore.client import BaseClient  # type: ignore
from fastapi import UploadFile

from app.core.integrations.storage.base import BaseS3Storage


class AvatarS3DataManager(BaseS3Storage):
    """
    Менеджер для работы с S3 хранилищем.
    Расширяет базовый класс для специфических нужд приложения.
    """

    def __init__(self, s3_client: BaseClient):
        super().__init__(s3_client)

    async def process_avatar(
        self,
        old_avatar_url: str,
        file: UploadFile,
        file_content: Optional[bytes] = None,
    ) -> str:
        """
        Процессинг аватара: удаление старого и загрузка нового

        Args:
            old_avatar_url (str): URL старого аватара (если есть)
            file (UploadFile): Новый файл аватара
            file_content (Optional[bytes], optional): Байтовое представление файла аватара (если есть). Defaults to None.

        Returns:
            str: URL нового аватара
        """
        # Удаление старого аватара если есть
        if old_avatar_url:
            try:
                file_key = old_avatar_url.split(f"{self.endpoint}/{self.bucket_name}/")[
                    1
                ]
                if await self.file_exists(file_key):
                    await self.delete_file(file_key)
            except Exception as e:
                self.logger.error("Ошибка удаления файла: %s", str(e))

        # Загрузка нового аватара
        result = await self.upload_file_from_content(
            file=file, file_content=file_content, file_key="avatars"
        )

        # Убедимся, что метод всегда возвращает строку
        if result is None:
            raise ValueError("Не удалось загрузить файл аватара")

        return result
