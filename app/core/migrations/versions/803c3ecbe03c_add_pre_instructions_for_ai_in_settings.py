"""add_pre_instructions_for_ai_in_settings

Revision ID: 803c3ecbe03c
Revises: d9bb096846fb
Create Date: 2025-04-13 13:56:47.091668

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "803c3ecbe03c"
down_revision: Union[str, None] = "d9bb096846fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "ai_settings", sa.Column("system_message", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("ai_settings", "system_message")
    # ### end Alembic commands ###
