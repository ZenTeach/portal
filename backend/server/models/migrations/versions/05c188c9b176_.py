"""Set knowledge_item on questions as nullable

Revision ID: 05c188c9b176
Revises: 9eac8ee98343
Create Date: 2021-09-08 19:03:46.155756

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '05c188c9b176'
down_revision = '9eac8ee98343'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('questions', 'knowledge_item',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=True)


def downgrade():
    op.alter_column('questions', 'knowledge_item',
                    existing_type=sa.VARCHAR(length=256),
                    nullable=False)
