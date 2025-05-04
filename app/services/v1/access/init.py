import json
from typing import Optional
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.access.service import AccessControlService

logger = logging.getLogger(__name__)


class PolicyInitService:
    """
    Сервис для инициализации базовых политик доступа.
    """

    def __init__(self, db_session: AsyncSession, access_service: Optional[AccessControlService] = None):
        """
        Инициализирует сервис инициализации политик.

        Args:
            db_session: Асинхронная сессия базы данных
        """
        self.db_session = db_session
        self.access_service = access_service or AccessControlService(db_session)

    async def initialize_default_policies(self, policies_dir: Path) -> int:
        """
        Инициализирует базовые политики доступа из JSON-файлов.

        Args:
            policies_dir: Путь к директории с JSON-файлами политик

        Returns:
            int: Количество созданных политик
        """
        # Проверяем, есть ли уже базовые политики
        existing_policies = await self.access_service.get_default_policies()
        if existing_policies:
            logger.info(
                f"Базовые политики уже существуют ({len(existing_policies)} шт.)"
            )
            return 0

        total_created = 0

        # Загружаем политики из JSON-файлов
        for policy_file in policies_dir.glob("*.json"):
            resource_type = policy_file.stem.replace("_policies", "")

            try:
                with open(policy_file, "r", encoding="utf-8") as f:
                    policies = json.load(f)

                for policy in policies:
                    # Устанавливаем флаг системной политики
                    policy["is_system"] = True

                    # Создаем базовую политику
                    created_policy = await self.access_service.create_default_policy(
                        policy
                    )
                    logger.info(
                        "Создана базовая политика: %s для %s",
                        created_policy.name,
                        resource_type
                    )
                    total_created += 1

            except Exception as e:
                logger.error(
                    "Ошибка при загрузке политик из файла %s: %s",
                    policy_file,
                    str(e)
                )

        return total_created

    async def apply_default_policies_to_workspace(
        self, workspace_id: int, owner_id: int
    ) -> int:
        """
        Применяет базовые политики к новому рабочему пространству.

        Args:
            workspace_id: ID рабочего пространства
            owner_id: ID владельца рабочего пространства

        Returns:
            int: Количество созданных политик
        """
        # Получаем все базовые политики
        default_policies = await self.access_service.get_default_policies()
        if not default_policies:
            logger.warning("Базовые политики не найдены")
            return 0

        total_created = 0

        # Создаем политики для рабочего пространства на основе базовых
        for default_policy in default_policies:
            try:
                # Создаем политику в рабочем пространстве
                policy = await self.access_service.create_workspace_policy_from_default(
                    default_policy_id=default_policy.id,
                    workspace_id=workspace_id,
                    owner_id=owner_id,
                )

                # Если это политика владельца рабочего пространства, применяем её к владельцу
                if (
                    default_policy.resource_type == "workspace"
                    and default_policy.priority >= 100
                ):
                    await self.access_service.apply_policy(
                        policy_id=policy.id,
                        resource_id=workspace_id,
                        subject_id=owner_id,
                        subject_type="user",
                    )

                total_created += 1

            except Exception as e:
                logger.error(
                    "Ошибка при создании политики %s для рабочего пространства %s: %s",
                    default_policy.name,
                    workspace_id,
                    str(e)
                )

        logger.info(
            "Создано %s политик для рабочего пространства %s",
            total_created,
            workspace_id
        )
        return total_created

    async def apply_default_resource_policy(
        self, resource_type: str, resource_id: int, workspace_id: int, owner_id: int
    ) -> bool:
        """
        Применяет базовую политику владельца к ресурсу.

        Args:
            resource_type: Тип ресурса
            resource_id: ID ресурса
            workspace_id: ID рабочего пространства
            owner_id: ID владельца ресурса

        Returns:
            bool: True, если политика успешно применена
        """
        # Получаем политики для данного типа ресурса в рабочем пространстве
        policies = await self.access_service.get_policies(
            workspace_id=workspace_id, resource_type=resource_type
        )

        # Ищем политику владельца (с наивысшим приоритетом)
        owner_policy = None
        for policy in policies:
            if policy.priority >= 100:
                owner_policy = policy
                break

        if not owner_policy:
            logger.warning(
                "Политика владельца для ресурса типа %s не найдена в рабочем пространстве %s",
                resource_type,
                workspace_id
            )
            return False

        # Применяем политику владельца к ресурсу
        try:
            await self.access_service.apply_policy(
                policy_id=owner_policy.id,
                resource_id=resource_id,
                subject_id=owner_id,
                subject_type="user",
            )
            logger.info(
                "Политика владельца (ID: %s) применена к ресурсу типа %s, ID: %s",
                owner_policy.id,
                resource_type,
                resource_id
            )
            return True

        except Exception as e:
            logger.error(
                "Ошибка при применении политики владельца к ресурсу типа %s, ID: %s: %s",
                resource_type,
                resource_id,
                str(e)
            )
            return False
