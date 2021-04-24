"""Add subjects model

Revision ID: 2aafaa8da1be
Revises: 7b901b99c924
Create Date: 2021-04-24 11:31:32.740714

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2aafaa8da1be'
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
