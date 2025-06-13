import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.v1 import TYPE_CHECKING
from app.models.v1.base import BaseModel

if TYPE_CHECKING:
    from app.models.v1.modules.templates import ModuleTemplateModel
    from app.models.v1.users import UserModel
    from app.models.v1.workspaces import WorkspaceModel


class ContentType(str, Enum):
    """
    Перечисление типов контента

    Attributes:
        TEXT (str): Текстовый контент
        IMAGE (str): Изображение
        VIDEO (str): Видео
        AUDIO (str): Аудио
        CODE (str): Код
    """

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"


class PostStatus(str, Enum):
    """
    Перечисление статусов поста

    Attributes:
        DRAFT (str): Черновик
        PUBLISHED (str): Опубликован
        ARCHIVED (str): Архивирован
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PostModel(BaseModel):
    """
    Модель поста в блоге

    Attributes:
        title (str): Заголовок поста.
        description (str): Описание поста.
        author_id (int): ID автора поста.
        status (PostStatus): Статус поста.
        views (int): Количество просмотров поста.
        content_blocks (list[PostContentBlockModel]): Список блоков контента поста.
        author (UserModel): Автор поста.
        workspace (WorkspaceModel): Рабочее пространство.
        tags (list[TagModel]): Список тегов, связанных с постом.

    Relationships:
        content_blocks (list[PostContentBlockModel]): Связь с блоками контента поста.
        author (UserModel): Связь с автором поста.
        tags (list[TagModel]): Связь с тегами, связанными с постом.
    """

    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[PostStatus] = mapped_column(default=PostStatus.DRAFT)
    views: Mapped[int] = mapped_column(default=0, nullable=False)

    content_blocks: Mapped[list["PostContentBlockModel"]] = relationship(
        "PostContentBlockModel",
        back_populates="post",
        order_by="PostContentBlockModel.order",
        cascade="all, delete-orphan",
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("module_templates.id", ondelete="SET NULL"), nullable=True
    )

    template: Mapped[Optional["ModuleTemplateModel"]] = relationship(
        "ModuleTemplateModel", back_populates="posts"
    )
    author: Mapped["UserModel"] = relationship("UserModel", back_populates="posts")
    tags: Mapped[list["TagModel"]] = relationship(
        secondary="post_tags", back_populates="posts"
    )

    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="posts"
    )


class TagModel(BaseModel):
    """
    Модель тега для блога

    Attributes:
        name (str): Название тега.

    Relationships:
        posts (list[PostModel]): Связь с постами, связанными с тегом.
    """

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    posts: Mapped[list["PostModel"]] = relationship(
        secondary="post_tags", back_populates="tags"
    )


class PostTagModel(BaseModel):
    """
    Связующая таблица постов и тегов

    Attributes:
        post_id (int): ID поста.
        tag_id (int): ID тега.

    Relationships (Многие-ко-многим):
        post (PostModel): Связь с постом.
        tag (TagModel): Связь с тегом.
    """

    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),)


class PostContentBlockModel(BaseModel):
    """
    Модель блока контента в посте блога

    Attributes:
        post_id (int): ID поста, к которому относится блок контента.
        type (ContentType): Тип контента.
        content (str): Контент блока.
        order (int): Порядковый номер блока.
        caption (str): Подпись к блоку.

    Relationships:
        post (PostModel): Связь с постом, к которому относится блок контента.
    """

    __tablename__ = "post_content_blocks"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    type: Mapped[ContentType] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)
    caption: Mapped[str] = mapped_column(nullable=True)

    post: Mapped["PostModel"] = relationship(
        "PostModel", back_populates="content_blocks"
    )
