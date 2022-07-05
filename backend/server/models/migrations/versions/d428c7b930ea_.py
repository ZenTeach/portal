""" Add private column in ClassQuiz

Revision ID: d428c7b930ea
Revises: 47e86327063b
Create Date: 2022-06-24 22:30:23.549629

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd428c7b930ea'
down_revision = '410b3bf0b1dd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('class_quiz', sa.Column(
        'private', sa.Boolean(), server_default='true', nullable=True))


def downgrade():
    op.drop_column('class_quiz', 'private')
