"""Migrate topic content translations

Revision ID: 85569e5dce20
Revises: 552d159b7bbf
Create Date: 2023-02-16 12:56:38.078826

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import HSTORE

# revision identifiers, used by Alembic.
revision = '85569e5dce20'
down_revision = '552d159b7bbf'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create extension hstore;')
    op.add_column('topics', sa.Column('value_translations', HSTORE(), nullable=True))


def downgrade():
    op.drop_column('topics', 'value_translations')
