import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.access import ResourceType
from app.models.v1.users import UserRole
from app.schemas.v1.access import AccessPolicyCreateRequestSchema
from app.schemas.v1.users import CurrentUserSchema
from app.services.v1.access.service import AccessControlService
from app.services.v1.base import BaseService
from app.core.settings import settings

class PolicyService(BaseService):
    """
    Сервис для управления политиками доступа.
    Предоставляет методы для создания и применения политик доступа.
    """

    def __init__(
        self,
        session: AsyncSession,
        access_service: Optional[AccessControlService] = None,
    ):
        """
        Инициализирует сервис политик доступа.

        Args:
            session: Асинхронная сессия базы данных
            access_service: Сервис контроля доступа
        """
        super().__init__(session)
        self.access_service = access_service or AccessControlService(session)
        self.policies_by_resource_type = self._load_policies()

    def _load_policies(self) -> Dict[str, List[Dict]]:
        """
        Загружает политики из JSON-файлов.

        Returns:
            Dict[str, List[Dict]]: Словарь политик по типам ресурсов
        """
        policies_dir = settings.paths.POLICIES_DIR
        policies_by_resource_type = {}

        for resource_type in ResourceType:
            file_path = policies_dir / f"{resource_type.value}_policies.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    policies_by_resource_type[resource_type.value] = json.load(f)
            else:
                self.logger.warning(f"Файл политик не найден: {file_path}")
                policies_by_resource_type[resource_type.value] = []

        return policies_by_resource_type

    async def create_default_policies(self, workspace_id: int, owner_id: int):
        """
        Создает базовые политики доступа для нового рабочего пространства.

        Args:
            workspace_id: ID рабочего пространства
            owner_id: ID владельца рабочего пространства
        """
        self.logger.info(
            f"Создание базовых политик доступа для рабочего пространства ID: {workspace_id}, "
            f"владелец ID: {owner_id}"
        )

        # Создаем политики для всех типов ресурсов
        for resource_type, policies in self.policies_by_resource_type.items():
            for policy_data in policies:
                policy_create_schema = AccessPolicyCreateRequestSchema(
                    name=policy_data["name"],
                    description=policy_data["description"],
                    resource_type=policy_data["resource_type"],
                    permissions=policy_data["permissions"],
                    priority=policy_data["priority"],
                    is_active=policy_data["is_active"],
                    workspace_id=workspace_id,
                    conditions=policy_data.get("conditions")
                )

                # Создаем политику
                policy_response = await self.access_service.create_policy(
                    policy_data=policy_create_schema,
                    current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN)
                )

                # Если это политика владельца рабочего пространства, применяем её к владельцу
                if (resource_type == ResourceType.WORKSPACE.value and
                    policy_data["priority"] >= 100):
                    await self.access_service.apply_policy(
                        policy_id=policy_response.data.id,
                        resource_id=workspace_id,
                        subject_id=owner_id,
                        subject_type="user"
                    )

        self.logger.info(
            f"Базовые политики доступа успешно созданы для рабочего пространства ID: {workspace_id}"
        )

    async def apply_default_access_rules(
        self,
        resource_type: ResourceType,
        resource_id: int,
        workspace_id: int,
        owner_id: int,
    ):
        """
        Применяет базовые правила доступа для нового ресурса.

        Args:
            resource_type: Тип ресурса
            resource_id: ID ресурса
            workspace_id: ID рабочего пространства
            owner_id: ID владельца ресурса
        """
        self.logger.info(
            f"Применение базовых правил доступа для ресурса типа {resource_type.value}, "
            f"ID: {resource_id}, рабочее пространство ID: {workspace_id}, владелец ID: {owner_id}"
        )

        # Получаем все политики для данного типа ресурса в рабочем пространстве
        policies = await self.access_service.get_policies(
            workspace_id=workspace_id,
            resource_type=resource_type.value,
            current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN),
        )

        # Применяем политику владельца к ресурсу
        for policy in policies:
            # Ищем политику с наивысшим приоритетом (обычно это политика владельца)
            if policy.priority >= 100:
                await self.access_service.apply_policy(
                    policy_id=policy.id,
                    resource_id=resource_id,
                    subject_id=owner_id,
                    subject_type="user",
                )
                self.logger.info(
                    f"Политика владельца (ID: {policy.id}) применена к ресурсу "
                    f"типа {resource_type.value}, ID: {resource_id}"
                )
                break
