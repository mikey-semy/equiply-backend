from typing import Any, Dict, List, Tuple, Optional
from io import BytesIO
import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks, UploadFile
from app.core.exceptions import (
    TableNotFoundError,
    InvalidFileFormatError,
    MissingRequiredColumnsError,
    DataConversionError,
    TableImportExportError
)
from app.core.integrations.storage.excel import ExcelS3DataManager
from app.models.v1.access import ResourceType
from app.models.v1.workspaces import WorkspaceRole
from app.schemas import (CurrentUserSchema, PaginationParams,
                         TableDefinitionDataSchema,
                         TableDefinitionCreateResponseSchema,
                         TableDefinitionDeleteResponseSchema,
                         TableDefinitionResponseSchema,
                         TableDefinitionUpdateResponseSchema,
                         TableImportResponseSchema)
from app.services.v1.access.init import PolicyInitService
from app.services.v1.base import BaseService
from app.services.v1.modules.tables.data_manager import TableDataManager
from app.services.v1.workspaces.data_manager import WorkspaceDataManager
from app.services.v1.workspaces.service import WorkspaceService


class TableService(BaseService):
    """
    Сервис для управления таблицами
    """

    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[ExcelS3DataManager] = None
    ):
        super().__init__(session)
        self.workspace_service = WorkspaceService(session)
        self.data_manager = TableDataManager(session)
        self.workspace_data_manager = WorkspaceDataManager(session)
        self.policy_init_service = PolicyInitService(self.session)
        self.s3_data_manager = s3_data_manager

    async def create_table(
        self,
        workspace_id: int,
        name: str,
        description: str,
        table_schema: Dict[str, Any],
        current_user: CurrentUserSchema,
    ) -> TableDefinitionCreateResponseSchema:
        """
        Создает новую таблицу в рабочем пространстве

        Args:
            workspace_id: ID рабочего пространства
            name: Название таблицы
            description: Описание таблицы
            table_schema: Схема таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionCreateResponseSchema: Созданная таблица

        Raises:
            WorkspaceNotFoundError: Если рабочее пространство не найдено
            ForbiddenError: Если у пользователя нет прав на создание таблицы
        """
        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Создание таблицы
        new_table = await self.data_manager.create_table(
            workspace_id=workspace_id,
            name=name,
            description=description,
            table_schema=table_schema,
        )

        # Применяем базовые правила доступа
        await self.policy_init_service.apply_default_resource_policy(
            resource_type=ResourceType.TABLE,
            resource_id=new_table.id,
            workspace_id=new_table.workspace_id,
            owner_id=current_user.id,
        )

        return TableDefinitionCreateResponseSchema(data=new_table)

    async def get_tables(
        self,
        workspace_id: int,
        current_user: CurrentUserSchema,
        pagination: PaginationParams,
        search: str = None,
    ) -> Tuple[List[TableDefinitionDataSchema], int]:
        """
        Получает список таблиц в рабочем пространстве.

        Args:
            workspace_id: ID рабочего пространства
            current_user: Текущий пользователь
            pagination: Параметры пагинации для постраничной загрузки результатов
            search: Необязательная строка поиска для фильтрации таблиц

        Returns:
            Кортеж, содержащий список таблиц и общее количество доступных таблиц
        """
        self.logger.info(
            "Пользователь %s (ID: %s) запросил список таблиц в рабочем пространстве %s. "
            "Параметры: пагинация=%s, поиск='%s'",
            current_user.username,
            current_user.id,
            workspace_id,
            pagination,
            search,
        )

        return await self.data_manager.get_tables(
            workspace_id=workspace_id,
            pagination=pagination,
            search=search,
        )

    async def get_table(
        self,
        workspace_id: int,
        table_id: int,
        current_user: CurrentUserSchema
    ) -> TableDefinitionResponseSchema:
        """
        Получает таблицу по ID.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionResponseSchema: Данные таблицы

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при запросе пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        self.logger.info(
            "Пользователь %s (ID: %s) получил информацию о таблице %s (ID: %s) из рабочего пространства %s",
            current_user.username,
            current_user.id,
            table.name,
            table_id,
            workspace_id,
        )

        return TableDefinitionResponseSchema(data=table)

    async def update_table(
        self,
        workspace_id: int,
        table_id: int,
        data: Dict[str, Any],
        current_user: CurrentUserSchema
    ) -> TableDefinitionUpdateResponseSchema:
        """
        Обновляет определение таблицы.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            data: Данные для обновления
            current_user: Текущий пользователь

        Returns:
            TableDefinitionUpdateResponseSchema: Обновленная таблица

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу для проверки существования и принадлежности к рабочему пространству
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при попытке обновления пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        # Обновляем таблицу
        updated_table = await self.data_manager.update_table(table_id, data)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил таблицу %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            updated_table.name,
            table_id,
            workspace_id,
        )

        return TableDefinitionUpdateResponseSchema(data=updated_table)

    async def delete_table(
        self,
        workspace_id: int,
        table_id: int,
        current_user: CurrentUserSchema
    ) -> TableDefinitionDeleteResponseSchema:
        """
        Удаляет таблицу.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionDeleteResponseSchema: Результат удаления

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Получаем таблицу для проверки существования и принадлежности к рабочему пространству
        table = await self.data_manager.get_table(table_id)

        if not table:
            self.logger.error(
                "Таблица с ID %s не найдена при попытке удаления пользователем %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)  # Используем то же исключение для безопасности

        # Удаляем таблицу
        success = await self.data_manager.delete_table(table_id)

        if not success:
            self.logger.error(
                "Не удалось удалить таблицу с ID %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        self.logger.info(
            "Пользователь %s (ID: %s) удалил таблицу с ID %s из рабочего пространства %s",
            current_user.username,
            current_user.id,
            table_id,
            workspace_id,
        )

        return TableDefinitionDeleteResponseSchema(
            message=f"Таблица с ID {table_id} успешно удалена"
        )

    async def import_from_excel(
        self,
        workspace_id: int,
        table_id: int,
        file_contents: bytes,
        filename: str,
        replace_existing: bool = False,
        background_tasks: Optional[BackgroundTasks] = None,
        current_user: CurrentUserSchema = None,
    ) -> TableImportResponseSchema:
        """
        Импортирует данные из Excel-файла в таблицу.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            file_contents: Содержимое Excel-файла в байтах
            filename: Имя загруженного файла
            replace_existing: Заменить существующие данные (если True) или добавить к существующим (если False)
            background_tasks: Объект для выполнения фоновых задач
            current_user: Текущий пользователь

        Returns:
            TableImportResponseSchema: Результат импорта

        Raises:
            TableNotFoundError: Если таблица не найдена
            InvalidFileFormatError: Если формат файла неверный
            MissingRequiredColumnsError: Если отсутствуют обязательные столбцы
            DataConversionError: Если возникли ошибки при преобразовании данных
            TableImportExportError: Если возникли другие ошибки при импорте
        """
        # Проверяем доступ к таблице
        table = await self.get_table(workspace_id, table_id, current_user)

        # Проверяем, что файл имеет расширение .xlsx или .xls
        if not filename.lower().endswith(('.xlsx', '.xls')):
            raise InvalidFileFormatError(filename)

        # Проверяем, что s3_data_manager инициализирован
        if not self.s3_data_manager:
            raise TableImportExportError(
                detail="S3 Data Manager не инициализирован",
                error_type="s3_manager_not_initialized"
            )

        try:
            # Создаем временный файл для загрузки в S3

            bytes_io = BytesIO(file_contents)
            file = UploadFile(file=bytes_io, filename=filename)
            file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            # Загружаем файл в S3
            file_url = await self.s3_data_manager.upload_file_from_content(
                file=file,
                file_key=f"tables/{table_id}/imports/{filename}"
            )

            # Читаем данные из Excel
            try:
                df = pd.read_excel(BytesIO(file_contents))
            except Exception as e:
                raise InvalidFileFormatError(
                    filename,
                    f"Excel (.xlsx, .xls). Ошибка: {str(e)}"
                )

            # Получаем схему таблицы
            table_schema = table.data.table_schema
            schema_properties = table_schema.get("properties", {})

            # Получаем названия столбцов из схемы
            schema_columns = {prop: details.get("title", prop) for prop, details in schema_properties.items()}

            # Проверяем наличие обязательных столбцов
            required_fields = table_schema.get("required", [])

            # Сопоставляем столбцы Excel с полями схемы
            excel_columns = df.columns.tolist()
            column_mapping = {}
            missing_required = []

            for field, title in schema_columns.items():
                if title in excel_columns:
                    column_mapping[title] = field
                elif field in excel_columns:
                    column_mapping[field] = field
                elif field in required_fields:
                    missing_required.append(field)

            if missing_required:
                raise MissingRequiredColumnsError(missing_required)

            # Преобразуем данные из DataFrame в список словарей
            rows_to_import = []
            conversion_errors = []

            for i, row in df.iterrows():
                try:
                    row_data = {}
                    for excel_col, schema_field in column_mapping.items():
                        if excel_col in row and not pd.isna(row[excel_col]):
                            # Преобразуем данные в соответствии с типом в схеме
                            field_type = schema_properties[schema_field].get("type")
                            value = row[excel_col]

                            if field_type == "number" or field_type == "integer":
                                try:
                                    value = float(value) if field_type == "number" else int(value)
                                except (ValueError, TypeError):
                                    conversion_errors.append(f"Строка {i+1}: значение '{value}' не может быть преобразовано в {field_type}")
                                    continue
                            elif field_type == "boolean":
                                if isinstance(value, bool):
                                    pass
                                elif isinstance(value, (int, float)):
                                    value = bool(value)
                                elif isinstance(value, str):
                                    value = value.lower() in ("true", "yes", "1", "да")

                            row_data[schema_field] = value

                    # Проверяем наличие всех обязательных полей
                    missing_fields = [field for field in required_fields if field not in row_data]
                    if missing_fields:
                        conversion_errors.append(f"Строка {i+1}: отсутствуют обязательные поля: {', '.join(missing_fields)}")
                        continue

                    rows_to_import.append(row_data)
                except Exception as e:
                    conversion_errors.append(f"Строка {i+1}: {str(e)}")

            # Если есть ошибки преобразования и нет данных для импорта, выбрасываем исключение
            if conversion_errors and not rows_to_import:
                raise DataConversionError(conversion_errors)

            # Если указано заменить существующие данные, удаляем их
            if replace_existing:
                await self.data_manager.delete_table_rows(table_id)

            # Сохраняем данные в таблицу через менеджер данных
            imported_count = 0
            if rows_to_import:
                imported_count = await self.data_manager.add_table_rows(table_id, rows_to_import)

            total_rows = len(df)

            # Формируем сообщение о результате
            if conversion_errors:
                message = f"Импортировано {imported_count} из {total_rows} строк. Обнаружены ошибки при преобразовании данных."
            else:
                message = f"Успешно импортировано {imported_count} строк."

            self.logger.info(
                "Пользователь %s (ID: %s) импортировал данные в таблицу %s (ID: %s) из файла %s. %s",
                current_user.username,
                current_user.id,
                table.data.name,
                table_id,
                filename,
                message
            )

            # Получаем обновленную таблицу
            updated_table = await self.data_manager.get_table(table_id)

            return TableImportResponseSchema(
                data=updated_table,
                message=message,
                imported_count=imported_count,
                total_count=total_rows,
                errors=conversion_errors if conversion_errors else None
            )
        except (InvalidFileFormatError, MissingRequiredColumnsError, DataConversionError) as e:
            # Пробрасываем специфические исключения
            raise
        except Exception as e:
            # Для других ошибок создаем общее исключение импорта/экспорта
            self.logger.error(f"Ошибка при импорте данных из Excel: {str(e)}")
            raise TableImportExportError(
                detail=f"Ошибка при импорте данных из Excel: {str(e)}",
                error_type="import_error",
                extra={"filename": filename}
            )

    async def export_to_excel(
        self,
        workspace_id: int,
        table_id: int,
        current_user: CurrentUserSchema,
    ) -> Tuple[bytes, str]:
        """
        Экспортирует данные таблицы в Excel-файл.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            current_user: Текущий пользователь

        Returns:
            Tuple[bytes, str]: Кортеж (содержимое Excel-файла в байтах, имя файла)

        Raises:
            TableNotFoundError: Если таблица не найдена
            TableImportExportError: Если возникли ошибки при экспорте
        """
        # Проверяем доступ к таблице
        table = await self.get_table(workspace_id, table_id, current_user)

        try:
            # Получаем данные таблицы через менеджер данных
            data_rows = await self.data_manager.get_table_rows(table_id)

            # Получаем схему таблицы
            table_schema = table.data.table_schema
            schema_properties = table_schema.get("properties", {})

            # Преобразуем схему в отображаемые названия столбцов
            column_titles = {}
            for field, details in schema_properties.items():
                column_titles[field] = details.get("title", field)

            # Создаем DataFrame из данных
            df = pd.DataFrame(data_rows)

            # Если есть данные, переименовываем столбцы
            if not df.empty and column_titles:
                # Переименовываем только те столбцы, которые есть в DataFrame
                rename_dict = {col: column_titles[col] for col in df.columns if col in column_titles}
                df = df.rename(columns=rename_dict)

            # Формируем имя файла
            filename = f"{table.data.name.replace(' ', '_')}_export.xlsx"

            # Создаем Excel-файл в памяти
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            file_content = buffer.getvalue()

            # Если S3 Data Manager инициализирован, сохраняем файл в S3
            if self.s3_data_manager:

                bytes_io = BytesIO(file_content)
                file = UploadFile(file=bytes_io, filename=filename)
                file.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                file_url = await self.s3_data_manager.upload_file_from_content(
                    file=file,
                    file_key=f"tables/{table_id}/exports/{filename}"
                )

                self.logger.info(f"Excel-файл сохранен в S3: {file_url}")

            self.logger.info(
                "Пользователь %s (ID: %s) экспортировал данные таблицы %s (ID: %s) в Excel-файл %s",
                current_user.username,
                current_user.id,
                table.data.name,
                table_id,
                filename
            )

            return file_content, filename
        except Exception as e:
            error_message = f"Ошибка при экспорте данных в Excel: {str(e)}"
            self.logger.error(error_message)

            raise TableImportExportError(
                detail=error_message,
                error_type="export_error",
                extra={"table_id": table_id}
            )
    
    async def create_row(
        self, 
        workspace_id: int,
        table_id: int, 
        data: Dict[str, Any], 
        current_user: CurrentUserSchema
    ) -> Dict[str, Any]:
        """
        Создает новую строку в таблице.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            data: Данные строки
            current_user: Текущий пользователь

        Returns:
            Dict[str, Any]: Созданная строка

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Проверяем доступ к таблице (это также проверит существование таблицы)
        table = await self.get_table(workspace_id, table_id, current_user)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.data.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.data.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Создаем строку через менеджер данных
        from app.models.v1.modules.tables import TableRowModel
    
        row = TableRowModel(table_definition_id=table_id, data=data)
        created_row = await self.data_manager.add_one(row)

        self.logger.info(
            "Пользователь %s (ID: %s) создал строку в таблице %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            table.data.name,
            table_id,
            workspace_id,
        )

        return created_row.data

    async def get_rows(
        self, 
        workspace_id: int,
        table_id: int, 
        pagination: PaginationParams, 
        current_user: CurrentUserSchema
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Получает строки таблицы с пагинацией.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            pagination: Параметры пагинации
            current_user: Текущий пользователь

        Returns:
            Tuple[List[Dict[str, Any]], int]: Список строк и общее количество

        Raises:
            TableNotFoundError: Если таблица не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Проверяем доступ к таблице (это также проверит существование таблицы)
        table = await self.get_table(workspace_id, table_id, current_user)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.data.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.data.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Получаем строки таблицы
        from app.models.v1.modules.tables import TableRowModel
        from sqlalchemy import select, func

        # Создаем базовый запрос для получения строк
        statement = select(TableRowModel).where(TableRowModel.table_definition_id == table_id)
    
        # Получаем общее количество строк
        count_query = select(func.count()).select_from(statement.subquery())
        total = await self.session.scalar(count_query) or 0
    
        # Применяем пагинацию
        statement = statement.offset(pagination.skip).limit(pagination.limit)
    
        # Получаем строки
        result = await self.session.execute(statement)
        rows = result.scalars().all()
    
        # Преобразуем в список словарей
        row_data = [row.data for row in rows]

        self.logger.info(
            "Пользователь %s (ID: %s) получил %s строк из таблицы %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            len(row_data),
            table.data.name,
            table_id,
            workspace_id,
        )

        return row_data, total

    async def update_row(
        self, 
        workspace_id: int,
        table_id: int,
        row_id: int, 
        data: Dict[str, Any], 
        current_user: CurrentUserSchema
    ) -> Dict[str, Any]:
        """
        Обновляет строку таблицы.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            row_id: ID строки
            data: Новые данные строки
            current_user: Текущий пользователь

        Returns:
            Dict[str, Any]: Обновленная строка

        Raises:
            TableNotFoundError: Если таблица не найдена
            RowNotFoundError: Если строка не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Проверяем доступ к таблице (это также проверит существование таблицы)
        table = await self.get_table(workspace_id, table_id, current_user)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.data.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.data.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Получаем строку
        from app.models.v1.modules.tables import TableRowModel
        from sqlalchemy import select
        from app.core.exceptions import RowNotFoundError

        statement = select(TableRowModel).where(
            (TableRowModel.id == row_id) & 
            (TableRowModel.table_definition_id == table_id)
        )
        result = await self.session.execute(statement)
        row = result.scalar_one_or_none()

        if not row:
            self.logger.error(
                "Строка с ID %s не найдена в таблице %s. Запрос от пользователя %s (ID: %s)",
                row_id,
                table_id,
                current_user.username,
                current_user.id,
            )
            raise RowNotFoundError(row_id)

        # Обновляем данные строки
        row.data = data
        await self.session.commit()
        await self.session.refresh(row)

        self.logger.info(
            "Пользователь %s (ID: %s) обновил строку %s в таблице %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            row_id,
            table.data.name,
            table_id,
            workspace_id,
        )

        return row.data

    async def delete_row(
        self, 
        workspace_id: int,
        table_id: int,
        row_id: int, 
        current_user: CurrentUserSchema
    ) -> bool:
        """
        Удаляет строку таблицы.

        Args:
            workspace_id: ID рабочего пространства
            table_id: ID таблицы
            row_id: ID строки
            current_user: Текущий пользователь

        Returns:
            bool: True, если строка успешно удалена

        Raises:
            TableNotFoundError: Если таблица не найдена
            RowNotFoundError: Если строка не найдена
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Проверяем доступ к таблице (это также проверит существование таблицы)
        table = await self.get_table(workspace_id, table_id, current_user)

        # Проверяем, что таблица принадлежит указанному рабочему пространству
        if table.data.workspace_id != workspace_id:
            self.logger.error(
                "Таблица с ID %s принадлежит рабочему пространству %s, а не %s. Запрос от пользователя %s (ID: %s)",
                table_id,
                table.data.workspace_id,
                workspace_id,
                current_user.username,
                current_user.id,
            )
            raise TableNotFoundError(table_id)

        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Удаляем строку
        from app.models.v1.modules.tables import TableRowModel
        from sqlalchemy import delete
        from app.core.exceptions import RowNotFoundError

        # Сначала проверяем существование строки
        from sqlalchemy import select
        check_statement = select(TableRowModel).where(
            (TableRowModel.id == row_id) & 
            (TableRowModel.table_definition_id == table_id)
        )
        result = await self.session.execute(check_statement)
        row = result.scalar_one_or_none()

        if not row:
            self.logger.error(
                "Строка с ID %s не найдена в таблице %s. Запрос от пользователя %s (ID: %s)",
                row_id,
                table_id,
                current_user.username,
                current_user.id,
            )
            raise RowNotFoundError(row_id)

        # Удаляем строку
        delete_statement = delete(TableRowModel).where(
            (TableRowModel.id == row_id) & 
            (TableRowModel.table_definition_id == table_id)
        )
        await self.session.execute(delete_statement)
        await self.session.commit()

        self.logger.info(
            "Пользователь %s (ID: %s) удалил строку %s из таблицы %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            row_id,
            table.data.name,
            table_id,
            workspace_id,
        )

        return True

    async def create_from_template(
        self, 
        workspace_id: int, 
        template_id: int, 
        current_user: CurrentUserSchema
    ) -> TableDefinitionDataSchema:
        """
        Создает таблицу из шаблона.

        Args:
            workspace_id: ID рабочего пространства
            template_id: ID шаблона таблицы
            current_user: Текущий пользователь

        Returns:
            TableDefinitionDataSchema: Созданная таблица

        Raises:
            TemplateNotFoundError: Если шаблон не найден
            WorkspaceAccessDeniedError: Если у пользователя нет доступа к рабочему пространству
        """
        # Проверяем доступ к рабочему пространству (требуется роль EDITOR или выше)
        await self.workspace_service.check_workspace_access(
            workspace_id, current_user, WorkspaceRole.EDITOR
        )

        # Получаем шаблон таблицы
        from app.core.exceptions import TemplateNotFoundError
        from app.models.v1.modules.tables import TableTemplateModel
        from sqlalchemy import select

        statement = select(TableTemplateModel).where(TableTemplateModel.id == template_id)
        result = await self.session.execute(statement)
        template = result.scalar_one_or_none()

        if not template:
            self.logger.error(
                "Шаблон таблицы с ID %s не найден. Запрос от пользователя %s (ID: %s)",
                template_id,
                current_user.username,
                current_user.id,
            )
            raise TemplateNotFoundError(template_id)

        # Создаем новую таблицу на основе шаблона
        new_table = await self.data_manager.create_table(
            workspace_id=workspace_id,
            name=f"{template.name} (копия)",
            description=template.description,
            table_schema=template.table_schema,
        )

        # Применяем базовые правила доступа
        await self.policy_init_service.apply_default_resource_policy(
            resource_type=ResourceType.TABLE,
            resource_id=new_table.id,
            workspace_id=new_table.workspace_id,
            owner_id=current_user.id,
        )

        # Если в шаблоне есть данные, копируем их в новую таблицу
        if hasattr(template, 'sample_data') and template.sample_data:
            await self.data_manager.add_table_rows(new_table.id, template.sample_data)

        self.logger.info(
            "Пользователь %s (ID: %s) создал таблицу %s (ID: %s) из шаблона %s (ID: %s) в рабочем пространстве %s",
            current_user.username,
            current_user.id,
            new_table.name,
            new_table.id,
            template.name,
            template_id,
            workspace_id,
        )

        return new_table
