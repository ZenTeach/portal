"""Add name to class_quiz table

Revision ID: 86cb068277cd
Revises: a87d0ba04464
Create Date: 2021-10-23 12:29:10.337925

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '86cb068277cd'
down_revision = 'a87d0ba04464'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('class_quiz', sa.Column('name', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('class_quiz', 'name')
