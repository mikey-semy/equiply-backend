from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WorkspaceMemberModel, WorkspaceModel, WorkspaceRole
from app.models.v1.access import (AccessPolicyModel, AccessRuleModel,
                                  DefaultPolicyModel, PermissionType,
                                  ResourceType, UserAccessSettingsModel)
from app.schemas import PaginationParams
from app.schemas.v1.access import (AccessPolicySchema, AccessRuleSchema,
                                   DefaultPolicySchema,
                                   UserAccessSettingsSchema)
from app.services.v1.base import BaseEntityManager
from app.core.decorators.permissions import transform_permissions

class AccessControlDataManager:
    """
    Менеджер данных для работы с системой контроля доступа.

    Управляет политиками доступа, правилами и настройками пользователей.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализирует менеджер данных для контроля доступа.

        Args:
            session: Асинхронная сессия базы данных
        """
        self.session = session
        self.policy_manager = BaseEntityManager(
            session=session, schema=AccessPolicySchema, model=AccessPolicyModel
        )
        self.rule_manager = BaseEntityManager(
            session=session, schema=AccessRuleSchema, model=AccessRuleModel
        )
        self.settings_manager = BaseEntityManager(
            session=session, schema=UserAccessSettingsSchema, model=UserAccessSettingsModel
        )
        self.default_policy_manager = BaseEntityManager(
            session=session, schema=DefaultPolicySchema, model=DefaultPolicyModel
        )

    # Методы для работы с политиками доступа
    @transform_permissions(input_param="policy_data", output_transform=True)
    async def create_policy(self, policy_data: dict) -> AccessPolicySchema:
        """
        Создает новую политику доступа.

        Args:
            policy_data: Данные для создания политики

        Returns:
            Созданная политика доступа
        """

        policy = self.policy_manager.model(**policy_data)
        return await self.policy_manager.add_item(policy)

    @transform_permissions(output_transform=True)
    async def get_policies_paginated(
        self, pagination: PaginationParams, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AccessPolicyModel], int]:
        """
        Получает список политик с фильтрацией и пагинацией.

        Args:
            pagination (PaginationParams): Параметры пагинации
            filters: Словарь фильтров для выборки политик

        Returns:
            tuple[List[AccessPolicyModel], int]: Список политик доступа и общее количество
        """
        # Создаем базовый запрос
        statement = select(AccessPolicyModel).distinct()

        # Применяем фильтры
        if filters:
            conditions = []
            for field, value in filters.items():
                if field == "workspace_id":
                    if value is None:
                        conditions.append(AccessPolicyModel.workspace_id.is_(None))
                    else:
                        conditions.append(AccessPolicyModel.workspace_id == value)
                elif field == "resource_type":
                    conditions.append(AccessPolicyModel.resource_type == value)
                elif field == "owner_id":
                    conditions.append(AccessPolicyModel.owner_id == value)
                elif field == "is_active":
                    conditions.append(AccessPolicyModel.is_active == value)
                elif field == "name":
                    conditions.append(AccessPolicyModel.name.ilike(f"%{value}%"))

            if conditions:
                statement = statement.where(and_(*conditions))

        # Используем общий метод для получения пагинированных записей
        return await self.policy_manager.get_paginated_items(statement, pagination)

    @transform_permissions(output_transform=True)
    async def get_policies_for_user_paginated(
        self,
        user_id: int,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[AccessPolicyModel], int]:
        """
        Получает список политик для конкретного пользователя с пагинацией.

        Args:
            user_id: ID пользователя
            pagination (PaginationParams): Параметры пагинации
            filters: Словарь фильтров для выборки политик

        Returns:
            tuple[List[AccessPolicyModel], int]: Список политик доступа и общее количество
        """
        # Создаем базовый запрос для получения политик пользователя
        # 1. Политики, созданные пользователем
        # 2. Публичные политики
        # 3. Политики в рабочих пространствах, где пользователь имеет доступ

        # Получаем рабочие пространства пользователя
        workspace_subquery = select(WorkspaceMemberModel.workspace_id).where(
            WorkspaceMemberModel.user_id == user_id
        )

        # Базовые условия
        conditions = [
            or_(
                AccessPolicyModel.owner_id == user_id,
                AccessPolicyModel.is_public is True,
                AccessPolicyModel.workspace_id.in_(workspace_subquery),
            ),
            AccessPolicyModel.is_active is True,
        ]

        # Применяем дополнительные фильтры
        if filters:
            for field, value in filters.items():
                if field == "workspace_id":
                    if value is None:
                        conditions.append(AccessPolicyModel.workspace_id.is_(None))
                    else:
                        conditions.append(AccessPolicyModel.workspace_id == value)
                elif field == "resource_type":
                    conditions.append(AccessPolicyModel.resource_type == value)
                elif field == "name":
                    conditions.append(AccessPolicyModel.name.ilike(f"%{value}%"))

        # Создаем запрос
        statement = select(AccessPolicyModel).distinct().where(and_(*conditions))

        # Используем общий метод для получения пагинированных записей
        return await self.policy_manager.get_paginated_items(statement, pagination)

    @transform_permissions(output_transform=True)
    async def get_policies(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AccessPolicySchema], int]:
        """
        Получает список всех политик с фильтрацией.

        Args:
            filters: Словарь фильтров для выборки политик

        Returns:
            List[AccessPolicyModel]: Список политик доступа
        """
        # Создаем базовый запрос
        statement = select(AccessPolicyModel).distinct()

        # Применяем фильтры
        if filters:
            conditions = []
            for field, value in filters.items():
                if field == "workspace_id":
                    if value is None:
                        conditions.append(AccessPolicyModel.workspace_id.is_(None))
                    else:
                        conditions.append(AccessPolicyModel.workspace_id == value)
                elif field == "resource_type":
                    conditions.append(AccessPolicyModel.resource_type == value)
                elif field == "owner_id":
                    conditions.append(AccessPolicyModel.owner_id == value)
                elif field == "is_active":
                    conditions.append(AccessPolicyModel.is_active == value)
                elif field == "name":
                    conditions.append(AccessPolicyModel.name.ilike(f"%{value}%"))
            if conditions:
                statement = statement.where(and_(*conditions))

        # Используем общий метод для получения всех записей
        return await self.policy_manager.get_items(statement)

    @transform_permissions(output_transform=True)
    async def get_policies_for_user(
        self, user_id: int, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AccessPolicySchema], int]:
        """
        Получает список всех политик, доступных пользователю.

        Args:
            user_id: ID пользователя
            filters: Словарь фильтров для выборки политик

        Returns:
            List[AccessPolicyModel]: Список политик доступа
        """
        # Создаем базовый запрос
        statement = select(AccessPolicyModel).distinct()

        # Добавляем условие для пользователя (политики в его рабочих пространствах или созданные им)
        user_condition = or_(
            AccessPolicyModel.owner_id == user_id,
            AccessPolicyModel.workspace_id.in_(
                select(WorkspaceModel.id).where(
                    WorkspaceModel.id.in_(
                        select(WorkspaceMemberModel.workspace_id).where(
                            WorkspaceMemberModel.user_id == user_id
                        )
                    )
                )
            ),
        )
        statement = statement.where(user_condition)

        # Применяем дополнительные фильтры
        if filters:
            conditions = []
            for field, value in filters.items():
                if field == "workspace_id":
                    if value is None:
                        conditions.append(AccessPolicyModel.workspace_id.is_(None))
                    else:
                        conditions.append(AccessPolicyModel.workspace_id == value)
                elif field == "resource_type":
                    conditions.append(AccessPolicyModel.resource_type == value)
                elif field == "is_active":
                    conditions.append(AccessPolicyModel.is_active == value)
                elif field == "name":
                    conditions.append(AccessPolicyModel.name.ilike(f"%{value}%"))
            if conditions:
                statement = statement.where(and_(*conditions))

        # Используем общий метод для получения всех записей
        return await self.policy_manager.get_items(statement)

    @transform_permissions(output_transform=True)
    async def get_policy(self, policy_id: int) -> Optional[AccessPolicySchema]:
        """
        Получает политику по ID.

        Args:
            policy_id: ID политики

        Returns:
            Политика доступа или None, если не найдена
        """
        return await self.policy_manager.get_item(policy_id)

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def update_policy(self, policy_id: int, policy_data: dict) -> AccessPolicySchema:
        """
        Обновляет политику доступа.

        Args:
            policy_id: ID политики
            policy_data: Данные для обновления

        Returns:
            Обновленная политика доступа
        """
        return await self.policy_manager.update_items(policy_id, policy_data)

    async def delete_policy(self, policy_id: int) -> bool:
        """
        Удаляет политику доступа.

        Args:
            policy_id: ID политики

        Returns:
            True, если политика успешно удалена
        """
        # Сначала удаляем все правила, связанные с политикой
        rules_statement = select(AccessRuleModel).where(
            AccessRuleModel.policy_id == policy_id
        )
        rules = await self.rule_manager.get_all(rules_statement)

        for rule in rules:
            await self.rule_manager.delete_item(rule.id)

        # Затем удаляем саму политику
        return await self.policy_manager.delete_item(policy_id)

    # Методы для работы с правилами доступа

    async def create_rule(self, rule_data: dict) -> AccessRuleSchema:
        """
        Создает новое правило доступа.

        Args:
            rule_data: Данные для создания правила

        Returns:
            Созданное правило доступа
        """
        rule = self.rule_manager.model(**rule_data)
        return await self.rule_manager.add_item(rule)

    async def get_rules_paginated(
        self, pagination: PaginationParams, filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[AccessRuleModel], int]:
        """
        Получает список правил с фильтрацией и пагинацией.

        Args:
            pagination (PaginationParams): Параметры пагинации
            filters: Словарь фильтров для выборки правил

        Returns:
            tuple[List[AccessRuleModel], int]: Список правил доступа и общее количество
        """
        # Создаем базовый запрос
        statement = select(AccessRuleModel).distinct()

        # Применяем фильтры
        if filters:
            conditions = []
            for field, value in filters.items():
                if field == "policy_id":
                    conditions.append(AccessRuleModel.policy_id == value)
                elif field == "resource_type":
                    conditions.append(AccessRuleModel.resource_type == value)
                elif field == "resource_id":
                    if value is None:
                        conditions.append(AccessRuleModel.resource_id.is_(None))
                    else:
                        conditions.append(AccessRuleModel.resource_id == value)
                elif field == "subject_id":
                    conditions.append(AccessRuleModel.subject_id == value)
                elif field == "subject_type":
                    conditions.append(AccessRuleModel.subject_type == value)

            if conditions:
                statement = statement.where(and_(*conditions))

        # Используем общий метод для получения пагинированных записей
        return await self.rule_manager.get_paginated_items(statement, pagination)

    async def get_rules_for_user_paginated(
        self,
        user_id: int,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[AccessRuleModel], int]:
        """
        Получает список правил доступа для пользователя с фильтрацией и пагинацией.

        Args:
            user_id: ID пользователя
            pagination (PaginationParams): Параметры пагинации
            filters: Словарь фильтров для выборки правил

        Returns:
            tuple[List[AccessRuleModel], int]: Список правил доступа и общее количество
        """
        # Создаем базовый запрос для получения правил
        # 1. Правила, созданные на основе политик пользователя
        policy_subquery = select(AccessPolicyModel.id).where(
            AccessPolicyModel.owner_id == user_id
        )

        # 2. Правила для рабочих пространств, где пользователь имеет роль ADMIN или MODERATOR
        workspace_subquery = select(WorkspaceMemberModel.workspace_id).where(
            and_(
                WorkspaceMemberModel.user_id == user_id,
                WorkspaceMemberModel.role.in_(
                    [WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.MODERATOR]
                ),
            )
        )

        # Объединяем условия
        statement = (
            select(AccessRuleModel)
            .distinct()
            .join(AccessPolicyModel, AccessRuleModel.policy_id == AccessPolicyModel.id)
            .where(
                or_(
                    AccessPolicyModel.owner_id == user_id,
                    AccessPolicyModel.id.in_(policy_subquery),
                    AccessPolicyModel.workspace_id.in_(workspace_subquery),
                    AccessPolicyModel.is_public is True,
                )
            )
        )

        # Применяем дополнительные фильтры
        if filters:
            conditions = []
            for field, value in filters.items():
                if field == "policy_id":
                    conditions.append(AccessRuleModel.policy_id == value)
                elif field == "resource_type":
                    conditions.append(AccessRuleModel.resource_type == value)
                elif field == "resource_id":
                    if value is None:
                        conditions.append(AccessRuleModel.resource_id.is_(None))
                    else:
                        conditions.append(AccessRuleModel.resource_id == value)
                elif field == "subject_id":
                    conditions.append(AccessRuleModel.subject_id == value)
                elif field == "subject_type":
                    conditions.append(AccessRuleModel.subject_type == value)

            if conditions:
                statement = statement.where(and_(*conditions))

        # Используем общий метод для получения пагинированных записей
        return await self.rule_manager.get_paginated_items(statement, pagination)

    async def get_rule(self, rule_id: int) -> Optional[AccessRuleSchema]:
        """
        Получает правило по ID.

        Args:
            rule_id: ID правила

        Returns:
            Правило доступа или None, если не найдено
        """
        return await self.rule_manager.get_item(rule_id)

    async def update_rule(self, rule_id: int, rule_data: dict) -> AccessRuleSchema:
        """
        Обновляет правило доступа.

        Args:
            rule_id: ID правила
            rule_data: Данные для обновления

        Returns:
            Обновленное правило доступа
        """
        return await self.rule_manager.update_items(rule_id, rule_data)

    async def delete_rule(self, rule_id: int) -> bool:
        """
        Удаляет правило доступа.

        Args:
            rule_id: ID правила

        Returns:
            True, если правило успешно удалено
        """
        return await self.rule_manager.delete_item(rule_id)

    async def get_rules_for_policy(self, policy_id: int) -> List[AccessRuleSchema]:
        """
        Получает список правил для конкретной политики.

        Args:
            policy_id: ID политики

        Returns:
            Список правил доступа для политики
        """
        statement = select(AccessRuleModel).where(
            AccessRuleModel.policy_id == policy_id
        )
        return await self.rule_manager.get_items(statement)

    # Методы для работы с разрешениями

    async def get_applicable_rules(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: Optional[int] = None,
    ) -> List[AccessRuleModel]:
        """
        Получает применимые правила для пользователя и ресурса.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса (опционально)

        Returns:
            Список применимых правил доступа
        """
        # Преобразуем resource_type в строку, если это перечисление
        resource_type_str = str(resource_type)

        # Получаем группы пользователя через базовый метод
        from app.models.v1.groups import UserGroupMemberModel
        from app.schemas.v1.groups.base import UserGroupMemberSchema

        # Создаем менеджер для работы с членством в группах
        group_member_manager = BaseEntityManager(
            self.session, UserGroupMemberSchema, UserGroupMemberModel
        )

        # Используем базовый метод для получения всех групп пользователя
        statement = select(UserGroupMemberModel).where(UserGroupMemberModel.user_id == user_id)
        user_group_members = await group_member_manager.get_all(statement)

        # Извлекаем ID групп
        user_group_ids = [member.group_id for member in user_group_members]

        # Формируем запрос для получения правил
        rules_statement = (
            select(AccessRuleModel)
            .join(AccessPolicyModel, AccessRuleModel.policy_id == AccessPolicyModel.id)
            .where(
                and_(
                    # Правило активно
                    AccessRuleModel.is_active is True,
                    # Политика активна
                    AccessPolicyModel.is_active is True,
                    # Правило для данного типа ресурса
                    AccessRuleModel.resource_type == resource_type_str,
                    # Правило для данного пользователя
                    or_(
                        and_(
                            AccessRuleModel.subject_type == "user",
                            AccessRuleModel.subject_id == user_id,
                        ),
                        and_(
                            AccessRuleModel.subject_type == "group",
                            AccessRuleModel.subject_id.in_(user_group_ids) if user_group_ids else False,
                        )
                    )
                )
            )
        )

        # Если указан конкретный ресурс, добавляем условие для него
        # или для правил, применимых ко всем ресурсам данного типа (resource_id is NULL)
        if resource_id is not None:
            rules_statement = rules_statement.where(
                or_(
                    AccessRuleModel.resource_id == resource_id,
                    AccessRuleModel.resource_id.is_(None),
                )
            )

        # Получаем правила
        rules = await self.rule_manager.get_all(rules_statement)

        return rules

    # Методы для работы с настройками пользователей

    async def get_user_settings(self, user_id: int) -> UserAccessSettingsSchema:
        """
        Получает настройки доступа пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Настройки доступа пользователя
        """
        statement = select(UserAccessSettingsModel).where(
            UserAccessSettingsModel.user_id == user_id
        )
        settings = await self.settings_manager.get_one(statement)

        if not settings:
            # Создаем настройки по умолчанию, если они не существуют
            settings = UserAccessSettingsModel(
                user_id=user_id,
                default_workspace_id=None,
                default_permission=PermissionType.READ,
            )
            await self.settings_manager.add_one(settings)

        return UserAccessSettingsSchema.model_validate(settings)

    async def update_user_settings(
        self, user_id: int, settings_data: dict
    ) -> UserAccessSettingsSchema:
        """
        Обновляет настройки доступа пользователя.

        Args:
            user_id: ID пользователя
            settings_data: Данные для обновления настроек

        Returns:
            Обновленные настройки доступа пользователя
        """
        statement = select(UserAccessSettingsModel).where(
            UserAccessSettingsModel.user_id == user_id
        )
        settings = await self.settings_manager.get_one(statement)

        if not settings:
            # Создаем настройки, если они не существуют
            new_settings_data = settings_data.model_dump(exclude_unset=True)
            new_settings_data["user_id"] = user_id
            settings = UserAccessSettingsModel(**new_settings_data)
            return await self.settings_manager.add_item(settings)

        # Обновляем существующие настройки
        update_data = settings_data.model_dump(exclude_unset=True)
        return await self.settings_manager.update_items(settings.id, update_data)

    # Методы для работы с базовыми политиками доступа

    @transform_permissions(output_transform=True, input_is_dict=True)
    async def get_default_policies(
        self, resource_type: Optional[str] = None
    ) -> List[DefaultPolicySchema]:
        """
        Получает список базовых политик доступа.

        Args:
            resource_type: Тип ресурса для фильтрации

        Returns:
            List[DefaultPolicySchema]: Список базовых политик
        """
        # Создаем базовый запрос
        statement = select(DefaultPolicyModel)

        # Применяем фильтр по типу ресурса, если указан
        if resource_type:
            statement = statement.where(
                DefaultPolicyModel.resource_type == resource_type
            )

        # Функция для преобразования permissions из словаря в список
        def transform_permissions_to_list(model):
            model_dict = model.__dict__.copy()
            if "permissions" in model_dict and isinstance(model_dict["permissions"], dict):
                from app.models.v1.base import BaseModel
                model_dict["permissions"] = BaseModel.dict_to_list_field(model_dict["permissions"])
            return model_dict
            # Используем базовый метод get_items для получения списка схем

        return await self.default_policy_manager.get_items(
            statement,
            transform_func=transform_permissions_to_list
        )

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def create_default_policy(self, policy_data: dict) -> DefaultPolicySchema:
        """
        Создает базовую политику доступа.

        Args:
            policy_data: Данные политики

        Returns:
            DefaultPolicySchema: Созданная политика
        """
        policy = self.default_policy_manager.model(**policy_data)
        return await self.default_policy_manager.add_item(policy)

    @transform_permissions(output_transform=True)
    async def get_default_policy(self, policy_id: int) -> Optional[DefaultPolicySchema]:
        """
        Получает базовую политику по ID.

        Args:
            policy_id: ID политики

        Returns:
            Optional[DefaultPolicySchema]: Найденная политика или None
        """
        return await self.default_policy_manager.get_item(policy_id)

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def update_default_policy(
        self, policy_id: int, policy_data: dict
    ) -> DefaultPolicySchema:
        """
        Обновляет базовую политику доступа.

        Args:
            policy_id: ID политики
            policy_data: Данные для обновления

        Returns:
            DefaultPolicySchema: Обновленная политика
        """
        # Используем базовый метод update_items для обновления и получения схемы
        return await self.default_policy_manager.update_items(policy_id, policy_data)

    async def delete_default_policy(self, policy_id: int) -> bool:
        """
        Удаляет базовую политику доступа.

        Args:
            policy_id: ID политики

        Returns:
            bool: True, если политика успешно удалена
        """
        # Проверяем, является ли политика системной
        policy = await self.get_default_policy(policy_id)
        if policy and policy.is_system:
            # Системные политики нельзя удалять
            return False

        # Используем базовый метод delete_item для удаления
        return await self.default_policy_manager.delete_item(policy_id)
