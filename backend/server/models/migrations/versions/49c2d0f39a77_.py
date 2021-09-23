"""Remove topic and knowledge_item columns from questions table

Revision ID: 49c2d0f39a77
Revises: e9d2cec81d58
Create Date: 2021-09-22 20:09:13.320435

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '49c2d0f39a77'
down_revision = 'e9d2cec81d58'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('questions', 'knowledge_item')
    op.drop_column('questions', 'topic')


def downgrade():
    op.add_column('questions', sa.Column('topic', sa.VARCHAR(
        length=256), autoincrement=False, nullable=True))
    op.add_column('questions', sa.Column('knowledge_item', sa.VARCHAR(
        length=256), autoincrement=False, nullable=True))
