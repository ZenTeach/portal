"""Add linked teacher_id to topics table

Revision ID: fd7224f6c813
Revises: 05c188c9b176
Create Date: 2021-09-10 18:10:06.060920

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fd7224f6c813'
down_revision = '05c188c9b176'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('topics', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'topics', 'teacher', ['teacher_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'topics', type_='foreignkey')
    op.drop_column('topics', 'teacher_id')
