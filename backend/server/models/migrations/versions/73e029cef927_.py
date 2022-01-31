"""Add topics table

Revision ID: 73e029cef927
Revises: 1575b17e8760
Create Date: 2021-07-24 15:33:10.654744

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '73e029cef927'
down_revision = '2028279d7185'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('topics',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('value', sa.VARCHAR(length=255),
                              autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name='knowledge_items_pkey')
                    )


def downgrade():
    op.drop_table('topics')
