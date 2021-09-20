"""Add teacher_id in knowledge_items table.

Revision ID: 173451ccb80e
Revises: bb1ac1a0f214
Create Date: 2021-09-20 22:37:06.359436

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '173451ccb80e'
down_revision = 'bb1ac1a0f214'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('knowledge_items', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'knowledge_items', 'teacher', ['teacher_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'knowledge_items', type_='foreignkey')
    op.drop_column('knowledge_items', 'teacher_id')
