"""Add subject_id to school_class

Revision ID: 91566f68862e
Revises: 4ec19fdb72d8
Create Date: 2021-04-24 17:25:57.458283

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '91566f68862e'
down_revision = '4ec19fdb72d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('school_class', sa.Column('subject_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('school_class', 'subject_id')
