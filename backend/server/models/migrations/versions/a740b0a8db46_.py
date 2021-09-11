"""Enable full-text search on topics

Revision ID: a740b0a8db46
Revises: fd7224f6c813
Create Date: 2021-09-11 08:53:58.301345

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a740b0a8db46'
down_revision = 'fd7224f6c813'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('topics', sa.Column('search_vector',
                  sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))


def downgrade():
    op.drop_column('topics', 'search_vector')
