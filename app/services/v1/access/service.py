from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.v1.access import AccessPolicyModel, AccessRuleModel, PermissionType, ResourceType
from app.models.v1.workspaces import WorkspaceRole
from app.services.v1.base import BaseService
from app.core.exceptions.access import AccessDeniedException

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

    async def check_permission(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        permission: Union[PermissionType, str],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Проверяет, имеет ли пользователь указанное разрешение для ресурса.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса
            permission: Тип разрешения
            context: Контекст выполнения (дополнительные атрибуты)

        Returns:
            bool: True, если доступ разрешен, иначе False
        """
        # Получаем все применимые правила доступа
        rules = await self.data_manager.get_applicable_rules(
            user_id, resource_type, resource_id
        )

        if not rules:
            # Если правил нет, проверяем базовые роли (RBAC)
            return await self._check_role_based_permission(
                user_id, resource_type, resource_id, permission
            )

        # Сортируем правила по приоритету
        sorted_rules = sorted(rules, key=lambda r: r.policy.priority, reverse=True)

        # Проверяем каждое правило
        for rule in sorted_rules:
            if await self._evaluate_rule(rule, permission, context):
                return True

        return False

    async def _check_role_based_permission(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int,
        permission: Union[PermissionType, str]
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
            from app.services.v1.workspaces.data_manager import WorkspaceDataManager
            workspace_manager = WorkspaceDataManager(self.session)
            role = await workspace_manager.check_user_workspace_role(workspace_id, user_id)

            if not role:
                # Проверяем, публичное ли рабочее пространство
                workspace = await workspace_manager.get_workspace(workspace_id)
                if workspace and workspace.is_public and permission == PermissionType.READ:
                    return True
                return False

            # Маппинг ролей на разрешения
            role_permissions = {
                WorkspaceRole.OWNER: [
                    PermissionType.READ, PermissionType.WRITE,
                    PermissionType.DELETE, PermissionType.MANAGE, PermissionType.ADMIN
                ],
                WorkspaceRole.ADMIN: [
                    PermissionType.READ, PermissionType.WRITE,
                    PermissionType.DELETE, PermissionType.MANAGE
                ],
                WorkspaceRole.MODERATOR: [
                    PermissionType.READ, PermissionType.WRITE, PermissionType.MANAGE
                ],
                WorkspaceRole.EDITOR: [PermissionType.READ, PermissionType.WRITE],
                WorkspaceRole.VIEWER: [PermissionType.READ]
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
        context: Optional[Dict[str, Any]] = None
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
        if str(permission) not in rule.policy.permissions:
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
        self,
        condition_key: str,
        condition_value: Any,
        context_value: Any
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
                except:
                    return False

            start_time = datetime.datetime.strptime(condition_value["start"], "%H:%M").time()
            end_time = datetime.datetime.strptime(condition_value["end"], "%H:%M").time()

            return start_time <= time_now <= end_time

        # Для простых условий проверяем равенство
        return condition_value == context_value

    async def _get_resource_workspace_id(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int
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
        context: Optional[Dict[str, Any]] = None
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
                    "permission": permission
                }
            )

    async def _get_resource_name(
        self,
        resource_type: Union[ResourceType, str],
        resource_id: int
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

    async def create_policy(
        self,
        name: str,
        resource_type: Union[ResourceType, str],
        permissions: List[Union[PermissionType, str]],
        conditions: Dict[str, Any] = None,
        description: str = None,
        priority: int = 0,
        owner_id: int = None,
        workspace_id: int = None
    ) -> AccessPolicyModel:
        """
        Создает новую политику доступа.

        Args:
            name: Название политики
            resource_type: Тип ресурса
            permissions: Список разрешений
            conditions: Условия применения политики
            description: Описание политики
            priority: Приоритет политики
            owner_id: ID владельца политики
            workspace_id: ID рабочего пространства (если применимо)

        Returns:
            AccessPolicyModel: Созданная политика
        """
        # Преобразуем разрешения в строки
        perm_strings = [str(p) for p in permissions]

        policy_data = {
            "name": name,
            "resource_type": str(resource_type),
            "permissions": perm_strings,
            "conditions": conditions or {},
            "description": description,
            "priority": priority,
            "owner_id": owner_id,
            "workspace_id": workspace_id,
            "is_active": True
        }

        return await self.data_manager.create_policy(policy_data)

    async def apply_policy(
        self,
        policy_id: int,
        resource_id: int,
        subject_id: int,
        subject_type: str = "user",
        attributes: Dict[str, Any] = None
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
            "is_active": True
        }

        return await self.data_manager.create_rule(rule_data)

    async def get_user_permissions(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int
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
        if await self._check_role_based_permission(user_id, resource_type, resource_id, PermissionType.READ):
            permissions.add(PermissionType.READ.value)

        if await self._check_role_based_permission(user_id, resource_type, resource_id, PermissionType.WRITE):
            permissions.add(PermissionType.WRITE.value)

        if await self._check_role_based_permission(user_id, resource_type, resource_id, PermissionType.DELETE):
            permissions.add(PermissionType.DELETE.value)

        if await self._check_role_based_permission(user_id, resource_type, resource_id, PermissionType.MANAGE):
            permissions.add(PermissionType.MANAGE.value)

        if await self._check_role_based_permission(user_id, resource_type, resource_id, PermissionType.ADMIN):
            permissions.add(PermissionType.ADMIN.value)

        return list(permissions)
