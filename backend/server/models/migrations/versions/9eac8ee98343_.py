"""Add a link between topic and knowledge item

Revision ID: 9eac8ee98343
Revises: 6df275844650
Create Date: 2021-08-25 18:30:11.910270

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '9eac8ee98343'
down_revision = '6df275844650'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('knowledge_items', sa.Column('topic_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'knowledge_items', 'topics', ['topic_id'], ['id'])


def downgrade():
    op.drop_constraint(None, 'knowledge_items', type_='foreignkey')
    op.drop_column('knowledge_items', 'topic_id')
