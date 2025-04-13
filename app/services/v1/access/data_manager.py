from typing import Any, Dict, List, Optional, Union
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.v1.access import AccessPolicyModel, AccessRuleModel, ResourceType
from app.services.v1.base import BaseEntityManager


class AccessControlDataManager(BaseEntityManager):
    """
    Менеджер данных для работы с политиками и правилами доступа.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=AccessPolicyModel, schema=None)

    async def get_policy(self, policy_id: int) -> Optional[AccessPolicyModel]:
        """
        Получает политику доступа по ID.

        Args:
            policy_id: ID политики

        Returns:
            Optional[AccessPolicyModel]: Найденная политика или None
        """
        return await self.session.get(AccessPolicyModel, policy_id)

    async def create_policy(self, policy_data: Dict[str, Any]) -> AccessPolicyModel:
        """
        Создает новую политику доступа.

        Args:
            policy_data: Данные политики

        Returns:
            AccessPolicyModel: Созданная политика
        """
        policy = AccessPolicyModel(**policy_data)
        self.session.add(policy)
        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def update_policy(
        self,
        policy_id: int,
        policy_data: Dict[str, Any]
    ) -> Optional[AccessPolicyModel]:
        """
        Обновляет политику доступа.

        Args:
            policy_id: ID политики
            policy_data: Данные для обновления

        Returns:
            Optional[AccessPolicyModel]: Обновленная политика или None
        """
        policy = await self.get_policy(policy_id)
        if not policy:
            return None

        for key, value in policy_data.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def delete_policy(self, policy_id: int) -> bool:
        """
        Удаляет политику доступа.

        Args:
            policy_id: ID политики

        Returns:
            bool: True, если политика успешно удалена, иначе False
        """
        policy = await self.get_policy(policy_id)
        if not policy:
            return False

        await self.session.delete(policy)
        await self.session.flush()
        return True

    async def get_rule(self, rule_id: int) -> Optional[AccessRuleModel]:
        """
        Получает правило доступа по ID.

        Args:
            rule_id: ID правила

        Returns:
            Optional[AccessRuleModel]: Найденное правило или None
        """
        return await self.session.get(AccessRuleModel, rule_id)

    async def create_rule(self, rule_data: Dict[str, Any]) -> AccessRuleModel:
        """
        Создает новое правило доступа.

        Args:
            rule_data: Данные правила

        Returns:
            AccessRuleModel: Созданное правило
        """
        rule = AccessRuleModel(**rule_data)
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def update_rule(
        self,
        rule_id: int,
        rule_data: Dict[str, Any]
    ) -> Optional[AccessRuleModel]:
        """
        Обновляет правило доступа.

        Args:
            rule_id: ID правила
            rule_data: Данные для обновления

        Returns:
            Optional[AccessRuleModel]: Обновленное правило или None
        """
        rule = await self.get_rule(rule_id)
        if not rule:
            return None

        for key, value in rule_data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> bool:
        """
        Удаляет правило доступа.

        Args:
            rule_id: ID правила

        Returns:
            bool: True, если правило успешно удалено, иначе False
        """
        rule = await self.get_rule(rule_id)
        if not rule:
            return False

        await self.session.delete(rule)
        await self.session.flush()
        return True

    async def get_applicable_rules(
        self,
        user_id: int,
        resource_type: Union[ResourceType, str],
        resource_id: int
    ) -> List[AccessRuleModel]:
        """
        Получает все применимые правила доступа для пользователя и ресурса.

        Args:
            user_id: ID пользователя
            resource_type: Тип ресурса
            resource_id: ID ресурса

        Returns:
            List[AccessRuleModel]: Список применимых правил
        """
        # Получаем группы пользователя
        user_groups = await self._get_user_groups(user_id)
        group_ids = [group.id for group in user_groups]

        # Формируем запрос для получения правил
        query = (
            select(AccessRuleModel)
            .options(joinedload(AccessRuleModel.policy))
            .where(
                and_(
                    AccessRuleModel.resource_type == str(resource_type),
                    AccessRuleModel.resource_id == resource_id,
                    AccessRuleModel.is_active == True,
                    # Правила для пользователя или для групп пользователя
                    (
                        (AccessRuleModel.subject_type == "user", AccessRuleModel.subject_id == user_id)
                        if not group_ids else
                        (
                            (AccessRuleModel.subject_type == "user", AccessRuleModel.subject_id == user_id) |
                            (AccessRuleModel.subject_type == "group", AccessRuleModel.subject_id.in_(group_ids))
                        )
                    )
                )
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def _get_user_groups(self, user_id: int) -> List[Any]:
        """
        Получает группы пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            List[Any]: Список групп пользователя
        """
        # Реализация зависит от вашей модели данных для групп пользователей
        # Пример:
        # from app.models.v1.users import UserGroupModel
        # query = select(UserGroupModel).where(UserGroupModel.user_id == user_id)
        # result = await self.session.execute(query)
        # return result.scalars().all()

        # Временная заглушка
        return []
