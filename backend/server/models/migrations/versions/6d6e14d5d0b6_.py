"""Add user created flag and associate teacher_id

Revision ID: 6d6e14d5d0b6
Revises: 86cb068277cd
Create Date: 2021-11-12 23:04:00.037096

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6d6e14d5d0b6'
down_revision = '86cb068277cd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('question_choice', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.add_column('question_choice', sa.Column('user_created', sa.Boolean(), nullable=True))
    op.create_foreign_key(None, 'question_choice', 'teacher', ['teacher_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'question_choice', type_='foreignkey')
    op.drop_column('question_choice', 'user_created')
    op.drop_column('question_choice', 'teacher_id')
