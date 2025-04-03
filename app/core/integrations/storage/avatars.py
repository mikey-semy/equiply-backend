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
        if (
            old_avatar_url
            and self.endpoint in old_avatar_url
            and self.bucket_name in old_avatar_url
        ):
            try:
                parts = old_avatar_url.split(f"{self.endpoint}/{self.bucket_name}/")
                if len(parts) > 1:
                    file_key = parts[1]
                    if await self.file_exists(file_key):
                        self.logger.info(f"Удаление старого аватара: {file_key}")
                        await self.delete_file(file_key)
            except Exception as e:
                self.logger.error("Ошибка удаления старого аватара: %s", str(e))
                # Продолжаем выполнение, даже если не удалось удалить старый аватар

        # Загрузка нового аватара
        try:
            result = await self.upload_file_from_content(
                file=file, file_content=file_content, file_key="avatars"
            )
            self.logger.info(f"Загружен новый аватар: {result}")
            return result
        except Exception as e:
            self.logger.error("Ошибка загрузки нового аватара: %s", str(e))
            raise ValueError(f"Не удалось загрузить файл аватара: {str(e)}")
