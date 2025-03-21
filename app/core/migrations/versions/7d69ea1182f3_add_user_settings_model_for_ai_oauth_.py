"""add user settings model for ai, oauth and etc

Revision ID: 7d69ea1182f3
Revises: 7290bbd5a6f1
Create Date: 2025-03-22 00:29:28.141541

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d69ea1182f3"
down_revision: Union[str, None] = "7290bbd5a6f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "ai_settings",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "preferred_model",
            sa.Enum(
                "YANDEX_GPT_LITE",
                "YANDEX_GPT_PRO",
                "YANDEX_GPT_PRO_32K",
                "LLAMA_8B",
                "LLAMA_70B",
                "CUSTOM",
                name="modeltype",
            ),
            nullable=False,
        ),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "module_templates",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("module_type", sa.String(length=50), nullable=False),
        sa.Column("schema", sa.JSON(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint("list_items_workspace_id_fkey", "list_items", type_="foreignkey")
    op.drop_column("list_items", "workspace_id")
    op.add_column("users", sa.Column("vk_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("yandex_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(None, "users", ["yandex_id"])
    op.create_unique_constraint(None, "users", ["vk_id"])
    op.create_unique_constraint(None, "users", ["google_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "yandex_id")
    op.drop_column("users", "google_id")
    op.drop_column("users", "vk_id")
    op.add_column(
        "list_items",
        sa.Column("workspace_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_foreign_key(
        "list_items_workspace_id_fkey",
        "list_items",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_table("module_templates")
    op.drop_table("ai_settings")
    # ### end Alembic commands ###
