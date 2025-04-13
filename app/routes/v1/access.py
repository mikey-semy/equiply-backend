from typing import List, Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import CurrentUserSchema
from app.schemas.v1.access.requests import PermissionCheckRequestSchema
from app.schemas.v1.access.responses import (
    PermissionCheckResponseSchema, UserPermissionsResponseSchema
)
from app.schemas.v1.access import (
    AccessPolicyCreateSchema, AccessPolicySchema, AccessPolicyUpdateSchema,
    AccessRuleCreateSchema, AccessRuleSchema, AccessRuleUpdateSchema
)
from app.schemas.v1.auth.exceptions import TokenMissingResponseSchema
from app.services.v1.access.service import AccessControlService


class AccessControlRouter(BaseRouter):
    """Маршруты для управления доступом."""

    def __init__(self):
        super().__init__(prefix="access", tags=["Access Control"])

    def configure(self):
        """Настройка маршрутов для управления доступом."""

        @self.router.post(
            path="/policies/",
            response_model=AccessPolicySchema,
            status_code=201,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def create_policy(
            policy_data: AccessPolicyCreateSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicySchema:
            """
            ## ➕ Создание политики доступа

            Создает новую политику доступа. Требуется роль администратора.

            ### Тело запроса:
            * **name**: Название политики
            * **resource_type**: Тип ресурса
            * **permissions**: Список разрешений
            * **description**: Описание политики (опционально)
            * **conditions**: Условия применения политики (опционально)
            * **priority**: Приоритет политики (опционально)
            * **workspace_id**: ID рабочего пространства (опционально)

            ### Returns:
            * Созданная политика доступа
            """
            return await access_service.create_policy(
                policy_data=policy_data,
                user=current_user
            )

        @self.router.get(
            path="/policies/",
            response_model=List[AccessPolicySchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def get_policies(
            access_service: FromDishka[AccessControlService],
            workspace_id: Optional[int] = Query(None, description="ID рабочего пространства"),
            resource_type: Optional[str] = Query(None, description="Тип ресурса"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> List[AccessPolicySchema]:
            """
            ## 📋 Получение списка политик доступа

            Возвращает список политик доступа. Администраторы видят все политики.
            Обычные пользователи видят только политики в своих рабочих пространствах.

            ### Args:
            * **workspace_id**: ID рабочего пространства (опционально)
            * **resource_type**: Тип ресурса (опционально)

            ### Returns:
            * Список политик доступа
            """
            return await access_service.get_policies_with_auth(
                user=current_user,
                workspace_id=workspace_id,
                resource_type=resource_type
            )

        @self.router.get(
            path="/policies/{policy_id}",
            response_model=AccessPolicySchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def get_policy(
            access_service: FromDishka[AccessControlService],
            policy_id: int = Path(..., description="ID политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicySchema:
            """
            ## 🔍 Получение политики доступа

            Возвращает информацию о политике доступа по её ID.

            ### Args:
            * **policy_id**: ID политики доступа

            ### Returns:
            * Данные политики доступа
            """
            return await access_service.get_policy_with_auth(
                policy_id=policy_id,
                user=current_user
            )

        @self.router.put(
            path="/policies/{policy_id}",
            response_model=AccessPolicySchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def update_policy(
            access_service: FromDishka[AccessControlService],
            policy_data: AccessPolicyUpdateSchema,
            policy_id: int = Path(..., description="ID политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicySchema:
            """
            ## ✏️ Обновление политики доступа

            Обновляет информацию о политике доступа.

            ### Args:
            * **policy_id**: ID политики доступа

            ### Тело запроса:
            * **name**: Новое название политики (опционально)
            * **description**: Новое описание политики (опционально)
            * **conditions**: Новые условия применения политики (опционально)
            * **permissions**: Новый список разрешений (опционально)
            * **priority**: Новый приоритет политики (опционально)
            * **is_active**: Новый флаг активности политики (опционально)

            ### Returns:
            * Обновленная политика доступа
            """
            return await access_service.update_policy_with_auth(
                policy_id=policy_id,
                policy_data=policy_data,
                user=current_user
            )

        @self.router.delete(
            path="/policies/{policy_id}",
            status_code=204,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def delete_policy(
            access_service: FromDishka[AccessControlService],
            policy_id: int = Path(..., description="ID политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> None:
            """
            ## 🗑️ Удаление политики доступа

            Удаляет политику доступа.

            ### Args:
            * **policy_id**: ID политики доступа
            """
            await access_service.delete_policy_with_auth(
                policy_id=policy_id,
                user=current_user
            )

        @self.router.post(
            path="/rules/",
            response_model=AccessRuleSchema,
            status_code=201,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def create_rule(
            rule_data: AccessRuleCreateSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleSchema:
            """
            ## ➕ Создание правила доступа

            Создает новое правило доступа на основе существующей политики.

            ### Тело запроса:
            * **policy_id**: ID политики доступа
            * **resource_id**: ID ресурса
            * **resource_type**: Тип ресурса
            * **subject_id**: ID субъекта (пользователя или группы)
            * **subject_type**: Тип субъекта ('user' или 'group')
            * **attributes**: Дополнительные атрибуты правила (опционально)

            ### Returns:
            * Созданное правило доступа
            """
            return await access_service.create_rule_with_auth(
                rule_data=rule_data,
                user=current_user
            )

        @self.router.get(
            path="/rules/",
            response_model=List[AccessRuleSchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def get_rules(
            access_service: FromDishka[AccessControlService],
            policy_id: Optional[int] = Query(None, description="ID политики"),
            resource_type: Optional[str] = Query(None, description="Тип ресурса"),
            resource_id: Optional[int] = Query(None, description="ID ресурса"),
            subject_id: Optional[int] = Query(None, description="ID субъекта"),
            subject_type: Optional[str] = Query(None, description="Тип субъекта"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> List[AccessRuleSchema]:
            """
            ## 📋 Получение списка правил доступа

            Возвращает список правил доступа с возможностью фильтрации.

            ### Args:
            * **policy_id**: ID политики (опционально)
            * **resource_type**: Тип ресурса (опционально)
            * **resource_id**: ID ресурса (опционально)
            * **subject_id**: ID субъекта (опционально)
            * **subject_type**: Тип субъекта (опционально)

            ### Returns:
            * Список правил доступа
            """
            return await access_service.get_rules_with_auth(
                user=current_user,
                policy_id=policy_id,
                resource_type=resource_type,
                resource_id=resource_id,
                subject_id=subject_id,
                subject_type=subject_type
            )

        @self.router.get(
            path="/rules/{rule_id}",
            response_model=AccessRuleSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def get_rule(
            access_service: FromDishka[AccessControlService],
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleSchema:
            """
            ## 🔍 Получение правила доступа

            Возвращает информацию о правиле доступа по его ID.

            ### Args:
            * **rule_id**: ID правила доступа

            ### Returns:
            * Данные правила доступа
            """
            return await access_service.get_rule_with_auth(
                rule_id=rule_id,
                user=current_user
            )

        @self.router.put(
            path="/rules/{rule_id}",
            response_model=AccessRuleSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def update_rule(
            access_service: FromDishka[AccessControlService],
            rule_data: AccessRuleUpdateSchema,
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleSchema:
            """
            ## ✏️ Обновление правила доступа

            Обновляет информацию о правиле доступа.

            ### Args:
            * **rule_id**: ID правила доступа

            ### Тело запроса:
            * **attributes**: Новые атрибуты правила (опционально)
            * **is_active**: Новый флаг активности правила (опционально)

            ### Returns:
            * Обновленное правило доступа
            """
            return await access_service.update_rule_with_auth(
                rule_id=rule_id,
                rule_data=rule_data,
                user=current_user
            )

        @self.router.delete(
            path="/rules/{rule_id}",
            status_code=204,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def delete_rule(
            access_service: FromDishka[AccessControlService],
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> None:
            """
            ## 🗑️ Удаление правила доступа

            Удаляет правило доступа.

            ### Args:
            * **rule_id**: ID правила доступа
            """
            await access_service.delete_rule_with_auth(
                rule_id=rule_id,
                user=current_user
            )

        @self.router.post(
            path="/check-permission/",
            response_model=PermissionCheckResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def check_permission(
            request: PermissionCheckRequestSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> PermissionCheckResponseSchema:
            """
            ## 🔒 Проверка разрешения

            Проверяет, имеет ли текущий пользователь указанное разрешение для ресурса.

            ### Тело запроса:
            * **resource_id**: ID ресурса
            * **permission**: Тип разрешения
            * **context**: Контекст выполнения (опционально)

            ### Returns:
            * Результат проверки разрешения
            """
            has_permission = await access_service.check_permission(
                user_id=current_user.id,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                permission=request.permission,
                context=request.context
            )

            return PermissionCheckResponseSchema(
                has_permission=has_permission,
                resource_type=str(request.resource_type),
                resource_id=request.resource_id,
                permission=str(request.permission)
            )

        @self.router.get(
            path="/user-permissions/{resource_type}/{resource_id}",
            response_model=UserPermissionsResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            }
        )
        @inject
        async def get_user_permissions(
            access_service: FromDishka[AccessControlService],
            resource_type: str = Path(..., description="Тип ресурса"),
            resource_id: int = Path(..., description="ID ресурса"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserPermissionsResponseSchema:
            """
            ## 🔑 Получение разрешений пользователя

            Получает список разрешений текущего пользователя для указанного ресурса.

            ### Args:
            * **resource_type**: Тип ресурса
            * **resource_id**: ID ресурса

            ### Returns:
            * Список разрешений пользователя для ресурса
            """
            permissions = await access_service.get_user_permissions(
                user_id=current_user.id,
                resource_type=resource_type,
                resource_id=resource_id
            )

            return UserPermissionsResponseSchema(
                resource_type=resource_type,
                resource_id=resource_id,
                permissions=permissions
            )
