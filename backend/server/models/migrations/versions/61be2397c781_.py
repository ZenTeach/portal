"""Add subjects model

Revision ID: 61be2397c781
Revises: 7b901b99c924
Create Date: 2021-04-20 08:54:48.102579

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '61be2397c781'
down_revision = '7b901b99c924'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('subjects',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=256), nullable=False),
                    sa.Column('enabled', sa.Boolean(), nullable=True),
                    sa.Column('remark', sa.String(length=256), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('subjects')
