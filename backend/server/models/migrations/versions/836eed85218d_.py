"""Add result_sent column to quiz_grade

Revision ID: 836eed85218d
Revises: d428c7b930ea
Create Date: 2022-07-07 19:50:59.750810

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '836eed85218d'
down_revision = 'd428c7b930ea'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('quiz_grade', sa.Column('result_sent', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('quiz_grade', 'result_sent')
