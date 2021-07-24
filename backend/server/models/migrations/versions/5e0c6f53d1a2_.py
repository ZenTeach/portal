"""Add knowledge_items table

Revision ID: 5e0c6f53d1a2
Revises: 73e029cef927
Create Date: 2021-07-24 15:35:37.302589

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '5e0c6f53d1a2'
down_revision = '73e029cef927'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('knowledge_items',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('value', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('knowledge_items')
