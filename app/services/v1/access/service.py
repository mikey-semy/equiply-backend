from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators.permissions import transform_permissions
from app.core.exceptions.access import AccessDeniedException
from app.models import (AccessRuleModel, PermissionType, ResourceType,
                        UserRole, WorkspaceRole)
from app.schemas import (AccessPolicyCreateRequestSchema,
                         AccessPolicyCreateResponseSchema,
                         AccessPolicyDeleteResponseSchema,
                         AccessPolicyResponseSchema, AccessPolicySchema,
                         AccessPolicyUpdateRequestSchema,
                         AccessPolicyUpdateResponseSchema,
                         AccessRuleCreateRequestSchema,
                         AccessRuleCreateResponseSchema,
                         AccessRuleDeleteResponseSchema,
                         AccessRuleResponseSchema, AccessRuleSchema,
                         AccessRuleUpdateRequestSchema,
                         AccessRuleUpdateResponseSchema, CurrentUserSchema,
                         DefaultPolicySchema, PaginationParams,
                         PermissionCheckDataSchema,
                         PermissionCheckResponseSchema,
                         UpdateUserAccessSettingsSchema,
                         UserAccessSettingsResponseSchema)
from app.services.v1.base import BaseService

from .data_manager import AccessControlDataManager


class AccessControlService(BaseService):
    """
    Сервис контроля доступа, объединяющий RBAC и ABAC подходы.

    Предоставляет методы для проверки прав доступа пользователей к ресурсам
    на основе ролей и атрибутов.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.data_manager = AccessControlDataManager(session)

    # Методы для работы с политиками доступа

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def create_policy(
        self,
        policy_data: AccessPolicyCreateRequestSchema,
        current_user: CurrentUserSchema,
    ) -> AccessPolicyCreateResponseSchema:
        """
        Создает новую политику доступа с проверкой прав пользователя.

        Args:
            policy_data: Данные политики
            current_user: Текущий авторизованный пользователь

        Returns:
            AccessPolicyCreateResponseSchema: Данные созданной политики
        """
        # Проверяем права на создание политики
        if current_user.role != UserRole.ADMIN:
            # Если указан workspace_id, проверяем права на управление этим рабочим пространством
            if policy_data.workspace_id:
                await self.authorize(
                    user_id=current_user.id,
                    resource_type=ResourceType.WORKSPACE,
                    resource_id=policy_data.workspace_id,
                    permission=PermissionType.MANAGE,
                )
            else:
                # Если workspace_id не указан, то это глобальная политика, требуются права админа
                raise AccessDeniedException(
                    message="Только администраторы могут создавать глобальные политики доступа",
                    extra={"user_id": current_user.id},
                )

        # Создаем словарь с данными политики
        policy_data_dict = policy_data.model_dump()

        # Преобразуем список разрешений в словарь
        permissions_dict = {str(perm): True for perm in policy_data.permissions}
        policy_data_dict["permissions"] = permissions_dict

        # Устанавливаем владельца политики
        policy_data_dict["owner_id"] = current_user.id

        # Создаем политику
        policy = await self.data_manager.create_policy(policy_data_dict)

        return AccessPolicyCreateResponseSchema(data=policy)

    @transform_permissions(output_transform=True)
    async def get_policies_paginated(
        self,
        pagination: PaginationParams,
        workspace_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        name: Optional[str] = None,
        current_user: CurrentUserSchema = None,
    ) -> tuple[List[AccessPolicySchema], int]:
        """
        Получает список политик доступа с возможностью пагинации, фильтрации и сортировки.

        Args:
            pagination (PaginationParams): Параметры пагинации
            workspace_id: ID рабочего пространства для фильтрации
            resource_type: Тип ресурса для фильтрации
            name: Поиск по названию политики
            current_user (CurrentUserSchema): Текущий авторизованный пользователь

        Returns:
            tuple[List[AccessPolicySchema], int]: Список политик доступа и общее количество

        """
        # Создаем словарь фильтров
        filters = {}
        if workspace_id is not None:
            filters["workspace_id"] = workspace_id
        if resource_type is not None:
            filters["resource_type"] = resource_type
        if name is not None:
            filters["name"] = name

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список политик доступа. Параметры: пагинация=%s, фильтры=%s",
            current_user.username,
            current_user.id,
            pagination,
            filters
        )

        # Администраторы видят все политики
        if current_user.role == UserRole.ADMIN:
            policies, total = await self.data_manager.get_policies_paginated(
                pagination=pagination, filters=filters
            )
        else:
            # Обычные пользователи видят только политики в своих рабочих пространствах
            # или созданные ими
            policies, total = await self.data_manager.get_policies_for_user_paginated(
                user_id=current_user.id, pagination=pagination, filters=filters
            )

        return [AccessPolicySchema.model_validate(policy) for policy in policies], total

    @transform_permissions(output_transform=True)
    async def get_policies(
        self,
        workspace_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        name: Optional[str] = None,
        current_user: CurrentUserSchema = None,
    ) -> List[AccessPolicySchema]:
        """
        Получает список всех политик доступа без пагинации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            workspace_id (int, optional): ID рабочего пространства для фильтрации.
            resource_type (str, optional): Тип ресурса для фильтрации.
            name: Поиск по названию политики
            current_user: Текущий авторизованный пользователь

        Returns:
            List[AccessPolicySchema]: Список политик доступа
        """
        # Создаем словарь фильтров
        filters = {}
        if workspace_id is not None:
            filters["workspace_id"] = workspace_id
        if resource_type is not None:
            filters["resource_type"] = resource_type
        if name is not None:
            filters["name"] = name

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список всех политик доступа. Фильтры: %s",
            current_user.username,
            current_user.id,
            filters
        )

        # Администраторы видят все политики
        if current_user.role == UserRole.ADMIN:
            policies = await self.data_manager.get_policies(
                filters=filters
            )
        else:
            # Обычные пользователи видят только политики в своих рабочих пространствах
            # или созданные ими
            policies = await self.data_manager.get_policies_for_user(
                user_id=current_user.id, filters=filters
            )

        return policies

    @transform_permissions(output_transform=True)
    async def get_policy(
        self, policy_id: int, current_user: CurrentUserSchema
    ) -> AccessPolicyResponseSchema:
        """
        Получает политику доступа по ID с проверкой прав.

        Args:
            policy_id: ID политики
            current_user: Текущий авторизованный пользователь

        Returns:
            AccessPolicyResponseSchema: Политика доступа

        Raises:
            ValueError: Если политика с указанным ID не найдена
            AccessDeniedException: Если у пользователя нет прав на просмотр политики
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил политику доступа с ID %s",
            current_user.username,
            current_user.id,
            policy_id
        )

        policy = await self.data_manager.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Политика с ID {policy_id} не найдена")

        # Проверяем права на просмотр политики
        if current_user.role != UserRole.ADMIN and policy.owner_id != current_user.id:
            if policy.workspace_id:
                # Проверяем, имеет ли пользователь доступ к рабочему пространству
                has_access = await self.check_permission(
                    user_id=current_user.id,
                    resource_type=ResourceType.WORKSPACE,
                    resource_id=policy.workspace_id,
                    permission=PermissionType.READ,
                )
                if not has_access:
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на просмотр политики {policy.name}",
                        extra={"user_id": current_user.id, "policy_id": policy_id},
                    )
            else:
                # Глобальные политики могут видеть только админы или их создатели
                raise AccessDeniedException(
                    message=f"Доступ запрещен: нет прав на просмотр политики {policy.name}",
                    extra={"user_id": current_user.id, "policy_id": policy_id},
                )
        self.logger.info("Политика с ID %s успешно получена", policy_id)

        return AccessPolicyResponseSchema(data=policy)

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def update_policy(
        self,
        policy_id: int,
        policy_data: AccessPolicyUpdateRequestSchema,
        current_user: CurrentUserSchema,
    ) -> AccessPolicyUpdateResponseSchema:
        """
        Обновляет политику доступа с проверкой прав.

        Args:
            policy_id: ID политики
            policy_data: Данные для обновления
            current_user: Текущий авторизованный пользователь

        Returns:
            AccessPolicySchema: Обновленная политика

        Raises:
            ValueError: Если политика с указанным ID не найдена
            AccessDeniedException: Если у пользователя нет прав на обновление политики
        """
        policy = await self.data_manager.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Политика с ID {policy_id} не найдена")

        # Проверяем права на обновление политики
        if current_user.role != UserRole.ADMIN and policy.owner_id != current_user.id:
            if policy.workspace_id:
                # Проверяем, имеет ли пользователь права администратора в рабочем пространстве
                has_access = await self.check_permission(
                    user_id=current_user.id,
                    resource_type=ResourceType.WORKSPACE,
                    resource_id=policy.workspace_id,
                    permission=PermissionType.MANAGE,
                )
                if not has_access:
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на обновление политики {policy.name}",
                        extra={"user_id": current_user.id, "policy_id": policy_id},
                    )
            else:
                # Глобальные политики могут обновлять только админы или их создатели
                raise AccessDeniedException(
                    message=f"Доступ запрещен: нет прав на обновление политики {policy.name}",
                    extra={"user_id": current_user.id, "policy_id": policy_id},
                )

        # Подготавливаем данные для обновления
        update_data = policy_data.model_dump(exclude_unset=True)

        # Если есть permissions, преобразуем список в словарь
        if "permissions" in update_data:
            permissions_dict = {str(perm): True for perm in update_data["permissions"]}
            update_data["permissions"] = permissions_dict

        # Обновляем политику
        updated_policy = await self.data_manager.update_policy(
            policy_id=policy_id, policy_data=update_data
        )

        return AccessPolicyUpdateResponseSchema(data=updated_policy)

    async def delete_policy(
        self, policy_id: int, current_user: CurrentUserSchema
    ) -> AccessPolicyDeleteResponseSchema:
        """
        Удаляет политику доступа с проверкой прав.

        Args:
            policy_id: ID политики
            current_user: Текущий авторизованный пользователь

        Returns:
            AccessPolicyDeleteResponseSchema: Данные об успешном удалении политики
        """
        policy = await self.data_manager.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Политика с ID {policy_id} не найдена")

        # Проверяем права на удаление политики
        if current_user.role != UserRole.ADMIN and policy.owner_id != current_user.id:
            if policy.workspace_id:
                # Проверяем, имеет ли пользователь права администратора в рабочем пространстве
                has_access = await self.check_permission(
                    user_id=current_user.id,
                    resource_type=ResourceType.WORKSPACE,
                    resource_id=policy.workspace_id,
                    permission=PermissionType.MANAGE,
                )
                if not has_access:
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на удаление политики {policy.name}",
                        extra={"user_id": current_user.id, "policy_id": policy_id},
                    )
            else:
                # Глобальные политики могут удалять только админы или их создатели
                raise AccessDeniedException(
                    message=f"Доступ запрещен: нет прав на удаление политики {policy.name}",
                    extra={"user_id": current_user.id, "policy_id": policy_id},
                )

        # Удаляем политику
        success = await self.data_manager.delete_policy(policy_id)
        if not success:
            raise ValueError(f"Не удалось удалить политику с ID {policy_id}")
        return AccessPolicyDeleteResponseSchema()

    # Методы для работы с правилами доступа

    async def create_rule(
        self, rule_data: AccessRuleCreateRequestSchema, current_user: CurrentUserSchema
    ) -> AccessRuleCreateResponseSchema:
        """
        Создает правило доступа с проверкой прав.

        Args:
            rule_data: Данные правила
            current_user: Текущий авторизованный пользователь

        Returns:
            AccessPolicyDeleteResponseSchema: Созданное правило
        """
        # Получаем политику, на основе которой создается правило
        policy = await self.data_manager.get_policy(rule_data.policy_id)
        if not policy:
            raise ValueError(f"Политика с ID {rule_data.policy_id} не найдена")

        # Проверяем права на создание правила
        if current_user.role != UserRole.ADMIN and policy.owner_id != current_user.id:
            if policy.workspace_id:
                # Проверяем, имеет ли пользователь права администратора в рабочем пространстве
                has_access = await self.check_permission(
                    user_id=current_user.id,
                    resource_type=ResourceType.WORKSPACE,
                    resource_id=policy.workspace_id,
                    permission=PermissionType.MANAGE,
                )
                if not has_access:
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на создание правила для политики {policy.name}",
                        extra={"user_id": current_user.id, "policy_id": policy.id},
                    )
            else:
                # Глобальные политики могут использовать только админы или их создатели
                raise AccessDeniedException(
                    message=f"Доступ запрещен: нет прав на создание правила для политики {policy.name}",
                    extra={"user_id": current_user.id, "policy_id": policy.id},
                )

        # Проверяем, что тип ресурса соответствует типу в политике
        if rule_data.resource_type != policy.resource_type:
            raise ValueError(
                f"Тип ресурса {rule_data.resource_type} не соответствует типу в политике {policy.resource_type}"
            )

        # Создаем правило
        rule_data_dict = rule_data.model_dump()
        rule = await self.data_manager.create_rule(rule_data_dict)

        return AccessRuleCreateResponseSchema(data=rule)

    async def get_rules(
        self,
        pagination: PaginationParams,
        policy_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        subject_type: Optional[str] = None,
        current_user: CurrentUserSchema = None,
    ) -> tuple[List[AccessRuleSchema], int]:
        """
        Получает список правил доступа с возможностью пагинации, фильтрации и сортировки.

        Args:
            pagination (PaginationParams): Параметры пагинации
            policy_id (int, optional): ID политики для фильтрации.
            resource_type (str, optional): Тип ресурса для фильтрации.
            resource_id: ID ресурса для фильтрации
            subject_id: ID субъекта для фильтрации
            subject_type: Тип субъекта для фильтрации
            current_user (CurrentUserSchema): Текущий авторизованный пользователь

        Returns:
            tuple[List[AccessRuleSchema], int]: Список правил доступа и общее количество

        Raises:
            ForbiddenError: Если у пользователя недостаточно прав для просмотра правил
        """
        # Создаем словарь фильтров
        filters = {}
        if policy_id is not None:
            filters["policy_id"] = policy_id
        if resource_type is not None:
            filters["resource_type"] = resource_type
        if resource_id is not None:
            filters["resource_id"] = resource_id
        if subject_id is not None:
            filters["subject_id"] = subject_id
        if subject_type is not None:
            filters["subject_type"] = subject_type

        self.logger.info(
            "Пользователь %s (ID: %s) запросил список правил доступа. Параметры: пагинация=%s, фильтры=%s",
            current_user.username,
            current_user.id,
            pagination,
            filters
        )
        # Администраторы видят все правила
        if current_user.role == UserRole.ADMIN:
            rules, total = await self.data_manager.get_rules_paginated(
                pagination=pagination, filters=filters
            )
        else:
            # Обычные пользователи видят только правила в своих рабочих пространствах
            # или созданные на основе их политик
            rules, total = await self.data_manager.get_rules_for_user_paginated(
                user_id=current_user.id, pagination=pagination, filters=filters
            )

        return [AccessRuleSchema.model_validate(rule) for rule in rules], total

    async def get_rule(
        self, rule_id: int, current_user: CurrentUserSchema
    ) -> AccessRuleResponseSchema:
        """
        Получает правило доступа по ID с проверкой прав.

        Args:
            rule_id: ID правила
            user: Текущий пользователь

        Returns:
            AccessRuleResponseSchema: Правило доступа
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил правило доступа с ID %s",
            current_user.username,
            current_user.id,
            rule_id
        )

        rule = await self.data_manager.get_rule(rule_id)
        if not rule:
            self.logger.warning("Правило с ID %s не найдено", rule_id)
            raise ValueError(f"Правило с ID {rule_id} не найдено")

        # Проверяем права на просмотр правила
        if current_user.role != UserRole.ADMIN:
            policy = rule.policy
            if policy.owner_id != current_user.id:
                if policy.workspace_id:
                    # Проверяем, имеет ли пользователь доступ к рабочему пространству
                    has_access = await self.check_permission(
                        user_id=current_user.id,
                        resource_type=ResourceType.WORKSPACE,
                        resource_id=policy.workspace_id,
                        permission=PermissionType.READ,
                    )
                    if not has_access:
                        raise AccessDeniedException(
                            message=f"Доступ запрещен: нет прав на просмотр правила {rule.id}",
                            extra={"user_id": current_user.id, "rule_id": rule_id},
                        )
                else:
                    # Глобальные правила могут видеть только админы или создатели политики
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на просмотр правила {rule.id}",
                        extra={"user_id": current_user.id, "rule_id": rule_id},
                    )

        self.logger.info("Правило с ID %s успешно получено", rule_id)
        return AccessRuleResponseSchema(data=rule)

    async def update_rule(
        self,
        rule_id: int,
        rule_data: AccessRuleUpdateRequestSchema,
        current_user: CurrentUserSchema,
    ) -> AccessRuleUpdateResponseSchema:
        """
        Обновляет правило доступа с проверкой прав.

        Args:
            rule_id: ID правила
            rule_data: Данные для обновления
            user: Текущий пользователь

        Returns:
            AccessRuleSchema: Обновленное правило
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил обновление правила с ID %s",
            current_user.username,
            current_user.id,
            rule_id
        )

        rule = await self.data_manager.get_rule(rule_id)
        if not rule:
            self.logger.warning("Правило с ID %s не найдено", rule_id)
            raise ValueError(f"Правило с ID {rule_id} не найдено")

        # Проверяем права на обновление правила
        if current_user.role != UserRole.ADMIN:
            policy = rule.policy
            if policy.owner_id != current_user.id:
                if policy.workspace_id:
                    # Проверяем, имеет ли пользователь права администратора в рабочем пространстве
                    has_access = await self.check_permission(
                        user_id=current_user.id,
                        resource_type=ResourceType.WORKSPACE,
                        resource_id=policy.workspace_id,
                        permission=PermissionType.MANAGE,
                    )
                    if not has_access:
                        raise AccessDeniedException(
                            message=f"Доступ запрещен: нет прав на обновление правила {rule.id}",
                            extra={"user_id": current_user.id, "rule_id": rule_id},
                        )
                else:
                    # Глобальные правила могут обновлять только админы или создатели политики
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на обновление правила {rule.id}",
                        extra={"user_id": current_user.id, "rule_id": rule_id},
                    )

        # Обновляем правило
        updated_rule = await self.data_manager.update_rule(
            rule_id=rule_id, rule_data=rule_data.model_dump(exclude_unset=True)
        )
        self.logger.info("Правило с ID %s успешно обновлено", rule_id)
        return AccessRuleUpdateResponseSchema(data=updated_rule)

    async def delete_rule(
        self, rule_id: int, current_user: CurrentUserSchema
    ) -> AccessRuleDeleteResponseSchema:
        """
        Удаляет правило доступа с проверкой прав.

        Args:
            rule_id: ID правила
            user: Текущий пользователь
        """
        rule = await self.data_manager.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Правило с ID {rule_id} не найдено")

        # Проверяем права на удаление правила
        if current_user.role != UserRole.ADMIN:
            policy = rule.policy
            if policy.owner_id != current_user.id:
                if policy.workspace_id:
                    # Проверяем, имеет ли пользователь права администратора в рабочем пространстве
                    has_access = await self.check_permission(
                        user_id=current_user.id,
                        resource_type=ResourceType.WORKSPACE,
                        resource_id=policy.workspace_id,
                        permission=PermissionType.MANAGE,
                    )
                    if not has_access:
                        raise AccessDeniedException(
                            message=f"Доступ запрещен: нет прав на удаление правила {rule.id}",
                            extra={"user_id": current_user.id, "rule_id": rule_id},
                        )
                else:
                    # Глобальные правила могут удалять только админы или создатели политики
                    raise AccessDeniedException(
                        message=f"Доступ запрещен: нет прав на удаление правила {rule.id}",
                        extra={"user_id": current_user.id, "rule_id": rule_id},
                    )

        # Удаляем правило
        success = await self.data_manager.delete_rule(rule_id)
        if not success:
            raise ValueError(f"Не удалось удалить правило с ID {rule_id}")
        return AccessRuleDeleteResponseSchema()

    # Методы для работы с разрешениями

    @transform_permissions(output_transform=True)
    async def get_user_permissions(
        self, user_id: int, resource_type: Union[ResourceType, str], resource_id: int
    ) -> List[str]:
        """
        Получает список разрешений пользователя для ресурса.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса

        Returns:
            List[str]: Список разрешений
        """
        # Получаем все применимые правила
        rules = await self.data_manager.get_applicable_rules(
            user_id, resource_type, resource_id
        )

        # Собираем все разрешения из правил
        permissions = set()
        for rule in rules:
            if rule.is_active and rule.policy.is_active:
                permissions.update(rule.policy.permissions)

        # Добавляем разрешения на основе роли
        if await self._check_role_based_permission(
            user_id, resource_type, resource_id, PermissionType.READ
        ):
            permissions.add(PermissionType.READ.value)

        if await self._check_role_based_permission(
            user_id, resource_type, resource_id, PermissionType.WRITE
        ):
            permissions.add(PermissionType.WRITE.value)

        if await self._check_role_based_permission(
            user_id, resource_type, resource_id, PermissionType.DELETE
        ):
            permissions.add(PermissionType.DELETE.value)

        if await self._check_role_based_permission(
            user_id, resource_type, resource_id, PermissionType.MANAGE
        ):
            permissions.add(PermissionType.MANAGE.value)

        if await self._check_role_based_permission(
            user_id, resource_type, resource_id, PermissionType.ADMIN
        ):
            permissions.add(PermissionType.ADMIN.value)

        return list(permissions)

    async def check_permission(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        permission: Union[PermissionType, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheckResponseSchema:
        """
        Проверяет, имеет ли пользователь указанное разрешение для ресурса.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса
            permission: Тип разрешения
            context: Контекст выполнения (дополнительные атрибуты)

        Returns:
            PermissionCheckResponseSchema: Результат проверки разрешения
        """
        # Получаем все применимые правила доступа
        rules = await self.data_manager.get_applicable_rules(
            user_id, resource_type, resource_id
        )

        if not rules:
            # Если правил нет, проверяем базовые роли (RBAC)
            has_permission = await self._check_role_based_permission(
                user_id, resource_type, resource_id, permission
            )
            return PermissionCheckResponseSchema(
                data=PermissionCheckDataSchema(
                    has_permission=has_permission,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    permission=permission,
                )
            )

        # Сортируем правила по приоритету
        sorted_rules = sorted(rules, key=lambda r: r.policy.priority, reverse=True)

        # Проверяем каждое правило
        for rule in sorted_rules:
            if await self._evaluate_rule(rule, permission, context):
                has_permission = True

        has_permission = False
        return PermissionCheckResponseSchema(
            data=PermissionCheckDataSchema(
                has_permission=has_permission,
                resource_type=resource_type,
                resource_id=resource_id,
                permission=permission,
            )
        )

    async def _check_role_based_permission(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        permission: Union[PermissionType, str],
    ) -> bool:
        """
        Проверяет разрешение на основе роли пользователя (RBAC).

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса
            permission: Тип разрешения

        Returns:
            bool: True, если доступ разрешен, иначе False
        """
        # Для рабочих пространств
        if resource_type == ResourceType.WORKSPACE:
            workspace_id = resource_id

            # Получаем роль пользователя в рабочем пространстве
            from app.services.v1.workspaces.data_manager import \
                WorkspaceDataManager

            workspace_manager = WorkspaceDataManager(self.session)
            role = await workspace_manager.check_user_workspace_role(
                workspace_id, user_id
            )

            if not role:
                # Проверяем, публичное ли рабочее пространство
                workspace = await workspace_manager.get_workspace(workspace_id)
                if (
                    workspace
                    and workspace.is_public
                    and permission == PermissionType.READ
                ):
                    return True
                return False

            # Маппинг ролей на разрешения
            role_permissions = {
                WorkspaceRole.OWNER: [
                    PermissionType.READ,
                    PermissionType.WRITE,
                    PermissionType.DELETE,
                    PermissionType.MANAGE,
                    PermissionType.ADMIN,
                ],
                WorkspaceRole.ADMIN: [
                    PermissionType.READ,
                    PermissionType.WRITE,
                    PermissionType.DELETE,
                    PermissionType.MANAGE,
                ],
                WorkspaceRole.MODERATOR: [
                    PermissionType.READ,
                    PermissionType.WRITE,
                    PermissionType.MANAGE,
                ],
                WorkspaceRole.EDITOR: [PermissionType.READ, PermissionType.WRITE],
                WorkspaceRole.VIEWER: [PermissionType.READ],
            }

            return permission in role_permissions.get(role, [])

        # Для других типов ресурсов (таблицы, списки и т.д.)
        # Сначала определяем, к какому рабочему пространству относится ресурс
        workspace_id = await self._get_resource_workspace_id(resource_type, resource_id)
        if not workspace_id:
            return False

        # Затем проверяем роль пользователя в этом рабочем пространстве
        return await self._check_role_based_permission(
            user_id, ResourceType.WORKSPACE, workspace_id, permission
        )

    async def _evaluate_rule(
        self,
        rule: AccessRuleModel,
        permission: Union[PermissionType, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Оценивает правило доступа с учетом контекста (ABAC).

        Args:
            rule: Правило доступа
            permission: Запрашиваемое разрешение
            context: Контекст выполнения

        Returns:
            bool: True, если правило разрешает доступ, иначе False
        """
        # Проверяем, активно ли правило
        if not rule.is_active or not rule.policy.is_active:
            return False

        # Проверяем, предоставляет ли политика запрашиваемое разрешение
        perm_str = str(permission)
        if (
            perm_str not in rule.policy.permissions
            or not rule.policy.permissions[perm_str]
        ):
            return False

        # Проверяем условия политики
        conditions = rule.policy.conditions

        # Если условий нет, разрешаем доступ
        if not conditions:
            return True

        # Проверяем каждое условие
        for condition_key, condition_value in conditions.items():
            # Если контекст не предоставлен или не содержит ключ условия
            if not context or condition_key not in context:
                # Для некоторых стандартных условий можем получить значение автоматически
                if condition_key == "time":
                    import datetime

                    context_value = datetime.datetime.now().time()
                elif condition_key == "date":
                    import datetime

                    context_value = datetime.datetime.now().date()
                else:
                    # Если не можем получить значение, считаем условие не выполненным
                    return False
            else:
                context_value = context[condition_key]

            # Проверяем соответствие условию
            if not self._check_condition(condition_key, condition_value, context_value):
                return False

        # Если все условия выполнены, разрешаем доступ
        return True

    def _check_condition(
        self, condition_key: str, condition_value: Any, context_value: Any
    ) -> bool:
        """
        Проверяет соответствие значения контекста условию.

        Args:
            condition_key: Ключ условия
            condition_value: Значение условия
            context_value: Значение из контекста

        Returns:
            bool: True, если условие выполнено, иначе False
        """
        # Обработка различных типов условий
        if condition_key == "role" and isinstance(condition_value, list):
            return context_value in condition_value

        elif condition_key == "time_range" and isinstance(condition_value, dict):
            import datetime

            if isinstance(context_value, datetime.time):
                time_now = context_value
            else:
                try:
                    time_now = datetime.datetime.strptime(context_value, "%H:%M").time()
                except ValueError:
                    return False

            start_time = datetime.datetime.strptime(
                condition_value["start"], "%H:%M"
            ).time()
            end_time = datetime.datetime.strptime(
                condition_value["end"], "%H:%M"
            ).time()

            return start_time <= time_now <= end_time

        # Для простых условий проверяем равенство
        return condition_value == context_value

    async def _get_resource_workspace_id(
        self, resource_type: Union[ResourceType, str], resource_id: int
    ) -> Optional[int]:
        """
        Определяет ID рабочего пространства, к которому относится ресурс.

        Args:
            resource_type: Тип ресурса
            resource_id: ID ресурса

        Returns:
            Optional[int]: ID рабочего пространства или None
        """
        if resource_type == ResourceType.TABLE:
            from app.models.v1.modules.tables import TableDefinitionModel

            result = await self.session.get(TableDefinitionModel, resource_id)
            return result.workspace_id if result else None

        elif resource_type == ResourceType.LIST:
            from app.models.v1.modules.lists import ListDefinitionModel

            result = await self.session.get(ListDefinitionModel, resource_id)
            return result.workspace_id if result else None

        elif resource_type == ResourceType.KANBAN:
            from app.models.v1.modules.kanban import KanbanBoardModel

            result = await self.session.get(KanbanBoardModel, resource_id)
            return result.workspace_id if result else None

        elif resource_type == ResourceType.POST:
            from app.models.v1.modules.posts import PostModel

            result = await self.session.get(PostModel, resource_id)
            return result.workspace_id if result else None

        return None

    async def authorize(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        permission: Union[PermissionType, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Авторизует действие пользователя, выбрасывая исключение при отказе.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса
            permission: Тип разрешения
            context: Контекст выполнения

        Raises:
            AccessDeniedException: Если доступ запрещен
        """
        has_permission = await self.check_permission(
            user_id, resource_type, resource_id, permission, context
        )

        if not has_permission:
            resource_name = await self._get_resource_name(resource_type, resource_id)
            raise AccessDeniedException(
                message=f"Доступ запрещен: недостаточно прав для {permission} к {resource_type} '{resource_name}'",
                extra={
                    "user_id": user_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "permission": permission,
                },
            )

    async def _get_resource_name(
        self, resource_type: Union[ResourceType, str], resource_id: int
    ) -> str:
        """
        Получает название ресурса для сообщений об ошибках.

        Args:
            resource_type: Тип ресурса
            resource_id: ID ресурса

        Returns:
            str: Название ресурса или его ID в виде строки
        """
        if resource_type == ResourceType.WORKSPACE:
            from app.models.v1.workspaces import WorkspaceModel

            result = await self.session.get(WorkspaceModel, resource_id)
            return result.name if result else str(resource_id)

        elif resource_type == ResourceType.TABLE:
            from app.models.v1.modules.tables import TableDefinitionModel

            result = await self.session.get(TableDefinitionModel, resource_id)
            return result.name if result else str(resource_id)

        # Аналогично для других типов ресурсов

        return str(resource_id)

    async def apply_policy(
        self,
        policy_id: int,
        resource_id: int,
        subject_id: int,
        subject_type: str = "user",
        attributes: Dict[str, Any] = None,
    ) -> AccessRuleModel:
        """
        Применяет политику к конкретному ресурсу и субъекту.

        Args:
            policy_id: ID политики
            resource_id: ID ресурса
            subject_id: ID субъекта (пользователя или группы)
            subject_type: Тип субъекта ("user" или "group")
            attributes: Дополнительные атрибуты правила

        Returns:
            AccessRuleModel: Созданное правило доступа
        """
        policy = await self.data_manager.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Политика с ID {policy_id} не найдена")

        rule_data = {
            "policy_id": policy_id,
            "resource_id": resource_id,
            "resource_type": policy.resource_type,
            "subject_id": subject_id,
            "subject_type": subject_type,
            "attributes": attributes or {},
            "is_active": True,
        }

        return await self.data_manager.create_rule(rule_data)

    async def get_user_settings(self, user_id: int) -> UserAccessSettingsResponseSchema:
        """
        Получает настройки доступа пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            UserAccessSettingsResponseSchema: Настройки доступа пользователя
        """
        settings = await self.data_manager.get_user_settings(user_id)
        return UserAccessSettingsResponseSchema(data=settings)

    async def update_user_settings(
        self, user_id: int, settings_data: UpdateUserAccessSettingsSchema
    ) -> UserAccessSettingsResponseSchema:
        """
        Обновляет настройки доступа пользователя.

        Args:
            user_id: ID пользователя
            settings_data: Данные для обновления настроек

        Returns:
            UserAccessSettingsResponseSchema: Обновленные настройки доступа пользователя
        """
        settings = await self.data_manager.update_user_settings(user_id, settings_data)
        return UserAccessSettingsResponseSchema(
            message="Настройки доступа пользователя успешно обновлены", data=settings
        )

    @transform_permissions(output_transform=True)
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
        return await self.data_manager.get_default_policies(resource_type)

    @transform_permissions(input_param="policy_data", output_transform=True)
    async def create_default_policy(self, policy_data: dict) -> DefaultPolicySchema:
        """
        Создает базовую политику доступа.

        Args:
            policy_data: Данные политики

        Returns:
            DefaultPolicySchema: Созданная политика
        """
        self.logger.debug(
            "Тип permissions перед созданием политики: %s, значение: %s",
            type(policy_data["permissions"]),
            policy_data["permissions"]
)
        return await self.data_manager.create_default_policy(policy_data)

    async def create_workspace_policies(self, workspace_id: int, owner_id: int) -> None:
        """
        Создает политики доступа для нового рабочего пространства на основе базовых политик.

        Args:
            workspace_id: ID рабочего пространства
            owner_id: ID владельца рабочего пространства
        """
        # Получаем все базовые политики
        default_policies = await self.get_default_policies()

        # Создаем политики для рабочего пространства
        for default_policy in default_policies:
            # Создаем схему для новой политики
            policy_data = AccessPolicyCreateRequestSchema(
                name=default_policy.name,
                description=default_policy.description,
                resource_type=default_policy.resource_type,
                permissions=default_policy.permissions,
                conditions=default_policy.conditions,
                priority=default_policy.priority,
                is_active=default_policy.is_active,
                is_public=default_policy.is_public,
                workspace_id=workspace_id,
            )

            # Создаем политику
            policy = await self.create_policy(
                policy_data=policy_data,
                current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN),
            )

            # Если это политика владельца рабочего пространства, применяем её к владельцу
            if (
                default_policy.resource_type == ResourceType.WORKSPACE.value
                and default_policy.priority >= 100
            ):
                await self.apply_policy(
                    policy_id=policy.data.id,
                    resource_id=workspace_id,
                    subject_id=owner_id,
                    subject_type="user",
                )

    @transform_permissions(output_transform=True)
    async def create_workspace_policy_from_default(
        self,
        default_policy_id: int,
        workspace_id: int,
        owner_id: int,
    ) -> AccessPolicySchema:
        """
        Создает политику доступа в рабочем пространстве на основе базовой политики.

        Args:
            default_policy_id: ID базовой политики
            workspace_id: ID рабочего пространства
            owner_id: ID владельца политики

        Returns:
            AccessPolicySchema: Созданная политика

        Raises:
            ValueError: Если базовая политика не найдена
        """
        # Получаем базовую политику
        default_policy = await self.data_manager.get_default_policy(default_policy_id)
        if not default_policy:
            raise ValueError(f"Базовая политика с ID {default_policy_id} не найдена")

        # Создаем данные для новой политики
        policy_data = AccessPolicyCreateRequestSchema(
            name=default_policy.name,
            description=default_policy.description,
            resource_type=default_policy.resource_type,
            permissions=default_policy.permissions,
            conditions=default_policy.conditions,
            priority=default_policy.priority,
            is_active=default_policy.is_active,
            workspace_id=workspace_id,
            owner_id=owner_id,
        )

        # Создаем политику
        policy_response = await self.create_policy(
            policy_data=policy_data,
            current_user=CurrentUserSchema(id=owner_id, role=UserRole.ADMIN),
        )

        return policy_response.data
