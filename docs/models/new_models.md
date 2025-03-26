```mermaid
erDiagram
    %% Пользователи и рабочие пространства
    UserModel ||--o{ WorkspaceModel : owns
    UserModel ||--o{ WorkspaceMemberModel : has_memberships
    UserModel ||--o{ PostModel : authors
    UserModel ||--o{ AISettingsModel : has_settings
    UserModel ||--o{ ModuleTemplateModel : creates

    WorkspaceModel ||--o{ WorkspaceMemberModel : has_members
    WorkspaceModel ||--o{ TableDefinitionModel : has_tables
    WorkspaceModel ||--o{ ListDefinitionModel : has_lists
    WorkspaceModel ||--o{ KanbanBoardModel : has_kanban_boards
    WorkspaceModel ||--o{ PostModel : has_posts
    WorkspaceModel ||--o{ ModuleIntegrationModel : has_integrations

    %% Модуль таблиц
    TableDefinitionModel ||--o{ TableRowModel : contains
    ModuleTemplateModel ||--o{ TableDefinitionModel : used_by

    %% Модуль списков
    ListDefinitionModel ||--o{ ListItemModel : contains
    ModuleTemplateModel ||--o{ ListDefinitionModel : used_by

    %% Модуль канбан-досок
    KanbanBoardModel ||--o{ KanbanColumnModel : has_columns
    KanbanColumnModel ||--o{ KanbanCardModel : has_cards
    ModuleTemplateModel ||--o{ KanbanBoardModel : used_by

    %% Модуль блога
    PostModel ||--o{ PostContentBlockModel : has_content_blocks
    PostModel }o--o{ TagModel : has_tags
    PostTagModel }|--|| PostModel : belongs_to_post
    PostTagModel }|--|| TagModel : belongs_to_tag
    ModuleTemplateModel ||--o{ PostModel : used_by

    %% Интеграции между модулями
    ModuleIntegrationModel ||--o{ LinkedItemModel : has_linked_items
    LinkedItemModel }o--o{ PostModel : links_to_post
    LinkedItemModel }o--o{ KanbanCardModel : links_to_kanban_card
    LinkedItemModel }o--o{ TableRowModel : links_to_table_row
    LinkedItemModel }o--o{ ListItemModel : links_to_list_item

    %% Перечисления
    UserRole ||--o{ UserModel : has_role
    WorkspaceRole ||--o{ WorkspaceMemberModel : has_role
    PostStatus ||--o{ PostModel : has_status
    ContentType ||--o{ PostContentBlockModel : has_type
    IntegrationType ||--o{ ModuleIntegrationModel : has_type
    ModelType ||--o{ AISettingsModel : has_model_type
    ModuleType ||--o{ ModuleTemplateModel : has_type

    %% Определения моделей с полями
    UserModel {
        int id
        str username
        str email
        str phone
        str hashed_password
        UserRole role
        str avatar
        bool is_active
        bool is_verified
        datetime created_at
        datetime updated_at
    }

    WorkspaceModel {
        int id
        str name
        str description
        int owner_id FK
        bool is_public
        datetime created_at
        datetime updated_at
    }

    WorkspaceMemberModel {
        int id
        int workspace_id FK
        int user_id FK
        WorkspaceRole role
        datetime created_at
        datetime updated_at
    }

    TableDefinitionModel {
        int id
        str name
        str description
        json schema
        json display_settings
        int workspace_id FK
        int template_id FK
        datetime created_at
        datetime updated_at
    }

    TableRowModel {
        int id
        int table_definition_id FK
        json data
        datetime created_at
        datetime updated_at
    }

    ListDefinitionModel {
        int id
        str name
        str description
        int workspace_id FK
        int template_id FK
        json schema
        json display_settings
        datetime created_at
        datetime updated_at
    }

    ListItemModel {
        int id
        int list_definition_id FK
        json data
        bool is_completed
        datetime created_at
        datetime updated_at
    }

    KanbanBoardModel {
        int id
        str name
        str description
        int workspace_id FK
        int template_id FK
        json settings
        datetime created_at
        datetime updated_at
    }

    KanbanColumnModel {
        int id
        int board_id FK
        str name
        str color
        int order
        json settings
        datetime created_at
        datetime updated_at
    }

    KanbanCardModel {
        int id
        int column_id FK
        str title
        str description
        int order
        json metadata
        datetime created_at
        datetime updated_at
    }

    PostModel {
        int id
        str title
        str description
        int author_id FK
        int workspace_id FK
        int template_id FK
        PostStatus status
        int views
        datetime created_at
        datetime updated_at
    }

    PostContentBlockModel {
        int id
        int post_id FK
        ContentType type
        str content
        int order
        str caption
        datetime created_at
        datetime updated_at
    }

    TagModel {
        int id
        str name
        datetime created_at
        datetime updated_at
    }

    PostTagModel {
        int post_id PK,FK
        int tag_id PK,FK
        datetime created_at
        datetime updated_at
    }

    AISettingsModel {
        int id
        int user_id FK
        ModelType model_type
        json settings
        datetime created_at
        datetime updated_at
    }

    ModuleTemplateModel {
        int id
        str name
        str description
        ModuleType module_type
        int creator_id FK
        json template_data
        bool is_public
        datetime created_at
        datetime updated_at
    }

    ModuleIntegrationModel {
        int id
        str name
        str description
        IntegrationType integration_type
        bool is_active
        json settings
        int workspace_id FK
        datetime created_at
        datetime updated_at
    }

    LinkedItemModel {
        int id
        int integration_id FK
        int post_id FK
        int kanban_card_id FK
        int table_row_id FK
        int list_item_id FK
        json metadata
        datetime created_at
        datetime updated_at
    }

    %% Перечисления с их значениями
    UserRole {
        str ADMIN
        str USER
        str GUEST
    }

    WorkspaceRole {
        str OWNER
        str ADMIN
        str EDITOR
        str VIEWER
    }

    PostStatus {
        str DRAFT
        str PUBLISHED
        str ARCHIVED
    }

    ContentType {
        str TEXT
        str IMAGE
        str VIDEO
        str AUDIO
        str CODE
    }

    IntegrationType {
        str KANBAN_TO_BLOG
        str TABLE_TO_BLOG
        str LIST_TO_BLOG
        str KANBAN_TO_LIST
        str TABLE_TO_KANBAN
    }

    ModelType {
        str GPT_3_5
        str GPT_4
        str CLAUDE
        str GEMINI
    }

    ModuleType {
        str KANBAN
        str TABLE
        str LIST
        str BLOG
    }


```

Эта диаграмма показывает все связи между твоими моделями:

1. Пользователи и рабочие пространства:

- Пользователь может владеть несколькими рабочими пространствами
- Пользователь может быть участником нескольких рабочих пространств
- Пользователь может быть автором нескольких постов

2. Рабочие пространства:

- Рабочее пространство может иметь несколько участников
- Рабочее пространство может содержать таблицы, списки, канбан-доски, посты
- Рабочее пространство может иметь несколько интеграций между модулями

3. Модули:

- Таблицы: Определение таблицы содержит строки
- Списки: Определение списка содержит элементы списка
- Канбан: Канбан-доска содержит колонки, которые содержат карточки
- Блог: Пост содержит блоки контента и может иметь теги

4. Интеграции:

- Интеграция может связывать различные элементы из разных модулей
- Связанный элемент может ссылаться на пост, карточку канбана, строку таблицы или элемент списка

Эта структура позволяет создавать гибкие рабочие пространства, где пользователи могут выбирать, какие модули им нужны, и настраивать интеграции между ними.