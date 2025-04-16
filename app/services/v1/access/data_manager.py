# from typing import List, Optional, Dict, Any
# from sqlalchemy import select, and_, or_, func, delete
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.v1.access import (
#     AccessPolicyModel, AccessRuleModel,
#     #UserAccessSettings,
#     ResourceType, PermissionType)
# from app.schemas.v1.access import (
#     AccessPolicySchema,
#     AccessRuleSchema,
#     # UserAccessSettingsSchema
# )
# from app.services.v1.base import BaseEntityManager

# class AccessControlDataManager:
#     """
#     Менеджер данных для работы с системой контроля доступа.

#     Управляет политиками доступа, правилами и настройками пользователей.
#     """

#     def __init__(self, session: AsyncSession):
#         """
#         Инициализирует менеджер данных для контроля доступа.

#         Args:
#             session: Асинхронная сессия базы данных
#         """
#         self.session = session
#         self.policy_manager = BaseEntityManager(session, AccessPolicySchema, AccessPolicyModel)
#         self.rule_manager = BaseEntityManager(session, AccessRuleSchema, AccessRuleModel)
#         self.settings_manager = BaseEntityManager(session,
#                                                   #UserAccessSettingsSchema,
#                                                   # UserAccessSettingsModel)
#                                                   )

#     # Методы для работы с политиками доступа

#     async def get_policies(self, filters: Optional[Dict[str, Any]] = None) -> List[AccessPolicySchema]:
#         """
#         Получает список политик с фильтрацией.

#         Args:
#             filters: Словарь фильтров для выборки политик

#         Returns:
#             Список политик доступа
#         """
#         statement = select(AccessPolicyModel)

#         if filters:
#             conditions = []
#             for field, value in filters.items():
#                 if field == 'workspace_id':
#                     if value is None:
#                         conditions.append(AccessPolicyModel.workspace_id.is_(None))
#                     else:
#                         conditions.append(AccessPolicyModel.workspace_id == value)
#                 elif field == 'owner_id':
#                     conditions.append(AccessPolicyModel.owner_id == value)
#                 elif field == 'is_active':
#                     conditions.append(AccessPolicyModel.is_active == value)
#                 elif field == 'name':
#                     conditions.append(AccessPolicyModel.name.ilike(f"%{value}%"))

#             if conditions:
#                 statement = statement.where(and_(*conditions))

#         return await self.policy_manager.get_items(statement)

#     async def get_policies_for_user(self, user_id: int, workspace_id: Optional[int] = None) -> List[AccessPolicySchema]:
#         """
#         Получает список политик для конкретного пользователя.

#         Args:
#             user_id: ID пользователя
#             workspace_id: ID рабочего пространства (опционально)

#         Returns:
#             Список политик доступа, доступных пользователю
#         """
#         conditions = [
#             or_(
#                 AccessPolicyModel.owner_id == user_id,
#                 AccessPolicyModel.is_public == True
#             ),
#             AccessPolicyModel.is_active == True
#         ]

#         if workspace_id is not None:
#             conditions.append(AccessPolicyModel.workspace_id == workspace_id)

#         statement = select(AccessPolicyModel).where(and_(*conditions))
#         return await self.policy_manager.get_items(statement)

#     async def get_policy(self, policy_id: int) -> Optional[AccessPolicySchema]:
#         """
#         Получает политику по ID.

#         Args:
#             policy_id: ID политики

#         Returns:
#             Политика доступа или None, если не найдена
#         """
#         return await self.policy_manager.get_item(policy_id)

#     async def create_policy(self, policy_data: dict) -> AccessPolicySchema:
#         """
#         Создает новую политику доступа.

#         Args:
#             policy_data: Данные для создания политики

#         Returns:
#             Созданная политика доступа
#         """
#         policy = AccessPolicyModel(**policy_data)
#         return await self.policy_manager.add_item(policy)

#     async def update_policy(self, policy_id: int, policy_data: dict) -> AccessPolicySchema:
#         """
#         Обновляет политику доступа.

#         Args:
#             policy_id: ID политики
#             policy_data: Данные для обновления

#         Returns:
#             Обновленная политика доступа
#         """
#         return await self.policy_manager.update_items(policy_id, policy_data)

#     async def delete_policy(self, policy_id: int) -> bool:
#         """
#         Удаляет политику доступа.

#         Args:
#             policy_id: ID политики

#         Returns:
#             True, если политика успешно удалена
#         """
#         # Сначала удаляем все правила, связанные с политикой
#         rules_statement = select(AccessRuleModel).where(AccessRuleModel.policy_id == policy_id)
#         rules = await self.rule_manager.get_all(rules_statement)

#         for rule in rules:
#             await self.rule_manager.delete_item(rule.id)

#         # Затем удаляем саму политику
#         return await self.policy_manager.delete_item(policy_id)

#     # Методы для работы с правилами доступа

#     async def get_rules(self, filters: Optional[Dict[str, Any]] = None) -> List[AccessRuleSchema]:
#         """
#         Получает список правил с фильтрацией.

#         Args:
#             filters: Словарь фильтров для выборки правил

#         Returns:
#             Список правил доступа
#         """
#         statement = select(AccessRuleModel)

#         if filters:
#             conditions = []
#             for field, value in filters.items():
#                 if field == 'policy_id':
#                     conditions.append(AccessRuleModel.policy_id == value)
#                 elif field == 'resource_type':
#                     conditions.append(AccessRuleModel.resource_type == value)
#                 elif field == 'resource_id':
#                     if value is None:
#                         conditions.append(AccessRuleModel.resource_id.is_(None))
#                     else:
#                         conditions.append(AccessRuleModel.resource_id == value)
#                 elif field == 'permission':
#                     conditions.append(AccessRuleModel.permission == value)

#             if conditions:
#                 statement = statement.where(and_(*conditions))

#         return await self.rule_manager.get_items(statement)

#     async def get_rules_for_policy(self, policy_id: int) -> List[AccessRuleSchema]:
#         """
#         Получает список правил для конкретной политики.

#         Args:
#             policy_id: ID политики

#         Returns:
#             Список правил доступа для политики
#         """
#         statement = select(AccessRuleModel).where(AccessRuleModel.policy_id == policy_id)
#         return await self.rule_manager.get_items(statement)

#     async def get_rule(self, rule_id: int) -> Optional[AccessRuleSchema]:
#         """
#         Получает правило по ID.

#         Args:
#             rule_id: ID правила

#         Returns:
#             Правило доступа или None, если не найдено
#         """
#         return await self.rule_manager.get_item(rule_id)

#     async def create_rule(self, rule_data: dict) -> AccessRuleSchema:
#         """
#         Создает новое правило доступа.

#         Args:
#             rule_data: Данные для создания правила

#         Returns:
#             Созданное правило доступа
#         """
#         rule = AccessRuleModel(**rule_data)
#         return await self.rule_manager.add_item(rule)

#     async def update_rule(self, rule_id: int, rule_data: dict) -> AccessRuleSchema:
#         """
#         Обновляет правило доступа.

#         Args:
#             rule_id: ID правила
#             rule_data: Данные для обновления

#         Returns:
#             Обновленное правило доступа
#         """
#         return await self.rule_manager.update_items(rule_id, rule_data)

#     async def delete_rule(self, rule_id: int) -> bool:
#         """
#         Удаляет правило доступа.

#         Args:
#             rule_id: ID правила

#         Returns:
#             True, если правило успешно удалено
#         """
#         return await self.rule_manager.delete_item(rule_id)

#     async def get_applicable_rules(
#         self,
#         user_id: int,
#         resource_type: ResourceType,
#         resource_id: Optional[int] = None
#     ) -> List[AccessRuleSchema]:
#         """
#         Получает применимые правила для пользователя и ресурса.

#         Args:
#             user_id: ID пользователя
#             resource_type: Тип ресурса
#             resource_id: ID ресурса (опционально)

#         Returns:
#             Список применимых правил доступа
#         """
#         # Получаем все активные политики, доступные пользователю
#         policies_statement = select(AccessPolicyModel).where(
#             and_(
#                 or_(
#                     AccessPolicyModel.owner_id == user_id,
#                     AccessPolicyModel.is_public == True
#                 ),
#                 AccessPolicyModel.is_active == True
#             )
#         )

#         policies = await self.policy_manager.get_all(policies_statement)
#         policy_ids = [policy.id for policy in policies]

#         if not policy_ids:
#             return []

#         # Получаем правила для этих политик, соответствующие типу ресурса
#         conditions = [
#             AccessRuleModel.policy_id.in_(policy_ids),
#             AccessRuleModel.resource_type == resource_type
#         ]

#         # Если указан конкретный ресурс, добавляем условие для него
#         # или для правил, применимых ко всем ресурсам данного типа (resource_id is NULL)
#         if resource_id is not None:
#             conditions.append(
#                 or_(
#                     AccessRuleModel.resource_id == resource_id,
#                     AccessRuleModel.resource_id.is_(None)
#                 )
#             )

#         rules_statement = select(AccessRuleModel).where(and_(*conditions))
#         return await self.rule_manager.get_items(rules_statement)

#     # Методы для работы с настройками пользователей

#     async def get_user_settings(self, user_id: int) -> UserAccessSettingsSchema:
#         """
#         Получает настройки доступа пользователя.

#         Args:
#             user_id: ID пользователя

#         Returns:
#             Настройки доступа пользователя
#         """
#         statement = select(UserAccessSettingsModel).where(UserAccessSettingsModel.user_id == user_id)
#         settings = await self.settings_manager.get_one(statement)

#         if not settings:
#             # Создаем настройки по умолчанию, если они не существуют
#             settings = UserAccessSettingsModel(
#                 user_id=user_id,
#                 default_workspace_id=None,
#                 default_permission=PermissionType.VIEW
#             )
#             await self.settings_manager.add_one(settings)

#         return UserAccessSettingsSchema.model_validate(settings)

#     async def update_user_settings(self, user_id: int, settings_data: dict) -> UserAccessSettingsSchema:
#         """
#         Обновляет настройки доступа пользователя.

#         Args:
#             user_id: ID пользователя
#             settings_data: Данные для обновления настроек

#         Returns:
#             Обновленные настройки доступа пользователя
#         """
#         statement = select(UserAccessSettingsModel).where(UserAccessSettingsModel.user_id == user_id)
#         settings = await self.settings_manager.get_one(statement)

#         if not settings:
#             # Создаем настройки, если они не существуют
#             settings_data['user_id'] = user_id
#             settings = UserAccessSettingsModel(**settings_data)
#             return await self.settings_manager.add_item(settings)

#         # Обновляем существующие настройки
#         return await self.settings_manager.update_items(settings.id, settings_data)
