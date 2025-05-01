from typing import List, Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Path, Query

from app.core.security.auth import get_current_user
from app.routes.base import BaseRouter
from app.schemas import CurrentUserSchema, Page, PaginationParams
from app.schemas.v1.access import (AccessPolicyCreateSchema,
                                   AccessPolicySchema,
                                   AccessPolicyUpdateSchema,
                                   AccessRuleCreateSchema, AccessRuleSchema,
                                   AccessRuleUpdateSchema)
from app.schemas.v1.access.requests import (PermissionCheckRequestSchema,
                                            UpdateUserAccessSettingsSchema)
from app.schemas.v1.access.responses import (AccessPolicyCreateResponseSchema,
                                             AccessPolicyDeleteResponseSchema,
                                             AccessPolicyListResponseSchema,
                                             AccessPolicyUpdateResponseSchema,
                                             AccessRuleCreateResponseSchema,
                                             AccessRuleDeleteResponseSchema,
                                             AccessRuleListResponseSchema,
                                             AccessRuleResponseSchema,
                                             AccessRuleUpdateResponseSchema,
                                             UserAccessSettingsResponseSchema,
                                             UserPermissionsResponseSchema)
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
            },
        )
        @inject
        async def create_policy(
            policy_data: AccessPolicyCreateSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicyCreateResponseSchema:
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
            * AccessPolicyCreateResponseSchema: Данные созданной политики
            """
            return await access_service.create_policy(
                policy_data=policy_data, current_user=current_user
            )

        @self.router.get(
            path="/policies/",
            response_model=List[AccessPolicySchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def get_policies(
            access_service: FromDishka[AccessControlService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: str = Query("created_at", description="Поле для сортировки"),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            workspace_id: Optional[int] = Query(
                None, description="ID рабочего пространства"
            ),
            resource_type: Optional[str] = Query(None, description="Тип ресурса"),
            name: Optional[str] = Query(None, description="Поиск по названию политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> List[AccessPolicySchema]:
            """
            ## 📋 Получение списка политик доступа

            Возвращает список политик доступа с пагинацией, фильтрацией и сортировкой.
            Администраторы видят все политики. Обычные пользователи видят только политики
            в своих рабочих пространствах или созданные ими.

            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **workspace_id**: ID рабочего пространства (опционально)
            * **resource_type**: Тип ресурса (опционально)
            * **name**: Поиск по названию политики (опционально)

            ### Returns:
            * Страница с политиками доступа
            """
            pagination = PaginationParams(
                skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
            )

            policies, total = await access_service.get_policies(
                pagination=pagination,
                workspace_id=workspace_id,
                resource_type=resource_type,
                name=name,
                current_user=current_user,
            )

            page = Page(
                items=policies, total=total, page=pagination.page, size=pagination.limit
            )

            return AccessPolicyListResponseSchema(data=page)

        @self.router.get(
            path="/policies/{policy_id}",
            response_model=AccessPolicySchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Политика не найдена",
                # },
                # 403: {
                #     "model": AccessDeniedResponseSchema,
                #     "description": "Доступ запрещен",
                # }
            },
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
            return await access_service.get_policy(
                policy_id=policy_id, current_user=current_user
            )

        @self.router.put(
            path="/policies/{policy_id}",
            response_model=AccessPolicySchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": AccessDeniedResponseSchema,
                #     "description": "Доступ запрещен",
                # },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Политика не найдена",
                # }
            },
        )
        @inject
        async def update_policy(
            access_service: FromDishka[AccessControlService],
            policy_data: AccessPolicyUpdateSchema,
            policy_id: int = Path(..., description="ID политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicyUpdateResponseSchema:
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
            * **is_public**: Новый флаг публичности политики (опционально)

            ### Returns:
            * Обновленная политика доступа
            """

            return await access_service.update_policy(
                policy_id=policy_id, policy_data=policy_data, current_user=current_user
            )

        @self.router.delete(
            path="/policies/{policy_id}",
            response_model=AccessPolicyDeleteResponseSchema,
            status_code=200,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": AccessDeniedResponseSchema,
                #     "description": "Доступ запрещен",
                # },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Политика не найдена",
                # }
            },
        )
        @inject
        async def delete_policy(
            access_service: FromDishka[AccessControlService],
            policy_id: int = Path(..., description="ID политики"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessPolicyDeleteResponseSchema:
            """
            ## 🗑️ Удаление политики доступа

            Удаляет политику доступа.

            ### Args:
            * **policy_id**: ID политики доступа
            ### Returns:
            * Сообщение об успешном удалении

            ### Raises:
            * **403**: Если у пользователя нет прав на удаление политики
            * **404**: Если политика с указанным ID не найдена
            """
            return await access_service.delete_policy(
                policy_id=policy_id, current_user=current_user
            )

        @self.router.post(
            path="/rules/",
            response_model=AccessRuleSchema,
            status_code=201,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": AccessDeniedResponseSchema,
                #     "description": "Доступ запрещен",
                # },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Политика не найдена",
                # },
                # 422: {
                #     "model": ValidationErrorResponseSchema,
                #     "description": "Ошибка валидации данных",
                # }
            },
        )
        @inject
        async def create_rule(
            rule_data: AccessRuleCreateSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleCreateResponseSchema:
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
            return await access_service.create_rule(
                rule_data=rule_data, current_user=current_user
            )

        @self.router.get(
            path="/rules/",
            response_model=List[AccessRuleSchema],
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": ForbiddenResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
            },
        )
        @inject
        async def get_rules(
            access_service: FromDishka[AccessControlService],
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            sort_by: str = Query("created_at", description="Поле для сортировки"),
            sort_desc: bool = Query(True, description="Сортировка по убыванию"),
            policy_id: Optional[int] = Query(None, description="ID политики"),
            resource_type: Optional[str] = Query(None, description="Тип ресурса"),
            resource_id: Optional[int] = Query(None, description="ID ресурса"),
            subject_id: Optional[int] = Query(None, description="ID субъекта"),
            subject_type: Optional[str] = Query(None, description="Тип субъекта"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleListResponseSchema:
            """
            ## 📋 Получение списка правил доступа

            Возвращает список правил доступа с пагинацией, фильтрацией и сортировкой.

            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **sort_by**: Поле для сортировки
            * **sort_desc**: Сортировка по убыванию
            * **policy_id**: ID политики (опционально)
            * **resource_type**: Тип ресурса (опционально)
            * **resource_id**: ID ресурса (опционально)
            * **subject_id**: ID субъекта (опционально)
            * **subject_type**: Тип субъекта (опционально)

            ### Returns:
            * Страница с правилами доступа
            """
            pagination = PaginationParams(
                skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
            )

            rules, total = await access_service.get_rules(
                pagination=pagination,
                policy_id=policy_id,
                resource_type=resource_type,
                resource_id=resource_id,
                subject_id=subject_id,
                subject_type=subject_type,
                current_user=current_user,
            )

            page = Page(
                items=rules, total=total, page=pagination.page, size=pagination.limit
            )

            return AccessRuleListResponseSchema(data=page)

        @self.router.get(
            path="/rules/{rule_id}",
            response_model=AccessRuleSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": ForbiddenResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Правило не найдено",
                # }
            },
        )
        @inject
        async def get_rule(
            access_service: FromDishka[AccessControlService],
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleResponseSchema:
            """
            ## 🔍 Получение правила доступа

            Возвращает информацию о правиле доступа по его ID.

            ### Args:
            * **rule_id**: ID правила доступа

            ### Returns:
            * Данные правила доступа
            """
            return await access_service.get_rule(
                rule_id=rule_id, current_user=current_user
            )

        @self.router.put(
            path="/rules/{rule_id}",
            response_model=AccessRuleSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                # 403: {
                #     "model": ForbiddenResponseSchema,
                #     "description": "Недостаточно прав для выполнения операции",
                # },
                # 404: {
                #     "model": NotFoundResponseSchema,
                #     "description": "Правило не найдено",
                # }
            },
        )
        @inject
        async def update_rule(
            access_service: FromDishka[AccessControlService],
            rule_data: AccessRuleUpdateSchema,
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleUpdateResponseSchema:
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
            return await access_service.update_rule(
                rule_id=rule_id, rule_data=rule_data, current_user=current_user
            )

        @self.router.delete(
            path="/rules/{rule_id}",
            response_model=AccessRuleDeleteResponseSchema,
            status_code=200,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                },
                #     403: {
                #         "model": ForbiddenResponseSchema,
                #         "description": "Недостаточно прав для выполнения операции",
                #     },
                #     404: {
                #         "model": NotFoundResponseSchema,
                #         "description": "Правило не найдено",
                #     }
            },
        )
        @inject
        async def delete_rule(
            access_service: FromDishka[AccessControlService],
            rule_id: int = Path(..., description="ID правила"),
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> AccessRuleDeleteResponseSchema:
            """
            ## 🗑️ Удаление правила доступа

            Удаляет правило доступа.

            ### Args:
            * **rule_id**: ID правила доступа
            """
            await access_service.delete_rule(rule_id=rule_id, current_user=current_user)

        @self.router.post(
            path="/check-permission/",
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def check_permission(
            request: PermissionCheckRequestSchema,
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> bool:
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
            await access_service.check_permission(
                user_id=current_user.id,
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                permission=request.permission,
                context=request.context,
            )

        @self.router.get(
            path="/user-permissions/{resource_type}/{resource_id}",
            response_model=UserPermissionsResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
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
                resource_id=resource_id,
            )

            return UserPermissionsResponseSchema(
                resource_type=resource_type,
                resource_id=resource_id,
                permissions=permissions,
            )

        @self.router.get(
            path="/settings/",
            response_model=UserAccessSettingsResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def get_user_access_settings(
            access_service: FromDishka[AccessControlService],
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserAccessSettingsResponseSchema:
            """
            ## 🔍 Получение настроек доступа пользователя

            Возвращает персональные настройки доступа текущего пользователя.

            ### Returns:
            * Настройки доступа пользователя
            """
            return await access_service.get_user_settings(current_user.id)

        @self.router.put(
            path="/settings/",
            response_model=UserAccessSettingsResponseSchema,
            responses={
                401: {
                    "model": TokenMissingResponseSchema,
                    "description": "Токен отсутствует",
                }
            },
        )
        @inject
        async def update_user_access_settings(
            access_service: FromDishka[AccessControlService],
            settings_data: UpdateUserAccessSettingsSchema,
            current_user: CurrentUserSchema = Depends(get_current_user),
        ) -> UserAccessSettingsResponseSchema:
            """
            ## ✏️ Обновление настроек доступа пользователя

            Обновляет персональные настройки доступа текущего пользователя.

            ### Тело запроса:
            * **default_workspace_id**: ID рабочего пространства по умолчанию (опционально)
            * **default_permission**: Разрешение по умолчанию для новых ресурсов (опционально)

            ### Returns:
            * Обновленные настройки доступа пользователя
            """
            return await access_service.update_user_settings(
                user_id=current_user.id, settings_data=settings_data
            )
