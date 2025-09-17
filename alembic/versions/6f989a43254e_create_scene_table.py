"""Create scene table

Revision ID: 6f989a43254e
Revises:
Create Date: 2025-09-09 11:10:47.390361

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f989a43254e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "scenes",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.Text, unique=True, index=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("modified_at", sa.DateTime, nullable=False),
        sa.Column("original_data", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("edit_prompt", sa.Text),
        sa.Column("result", sa.Text),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("scenes")
