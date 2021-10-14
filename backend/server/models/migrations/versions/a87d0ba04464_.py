"""Remove non-null contraint on question tags

Revision ID: a87d0ba04464
Revises: ffc6a2fa3fbb
Create Date: 2021-10-14 15:36:29.227188

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a87d0ba04464'
down_revision = 'ffc6a2fa3fbb'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('questions', 'tag',
                    existing_type=sa.VARCHAR(length=128),
                    nullable=True)


def downgrade():
    op.alter_column('questions', 'tag',
                    existing_type=sa.VARCHAR(length=128),
                    nullable=False)
