"""Add users table

Revision ID: 33a9b88c44bb
Revises: 552d159b7bbf
Create Date: 2022-09-01 22:15:44.339403

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '33a9b88c44bb'
down_revision = '552d159b7bbf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('updated', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('type', sa.String(length=50), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('users')
