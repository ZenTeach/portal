"""Enable full-text search on knowledge item

Revision ID: 9fdde5131a0f
Revises: 173451ccb80e
Create Date: 2021-09-21 20:36:47.671006

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = '9fdde5131a0f'
down_revision = '173451ccb80e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('knowledge_items', sa.Column('search_vector',
                  sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))


def downgrade():
    op.drop_column('knowledge_items', 'search_vector')
