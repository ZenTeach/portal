"""Add key_stage to school_class table

Revision ID: 2028279d7185
Revises: 009655ab4286
Create Date: 2021-06-08 22:45:38.902711

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2028279d7185'
down_revision = '009655ab4286'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('school_class', sa.Column('key_stage', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('school_class', 'key_stage')
