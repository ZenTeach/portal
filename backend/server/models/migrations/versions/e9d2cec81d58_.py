"""Sync and update search vectors for knowledge item

Revision ID: e9d2cec81d58
Revises: 9fdde5131a0f
Create Date: 2021-09-21 20:38:48.096188

"""
from alembic import op
from sqlalchemy_searchable import sync_trigger, vectorizer

# revision identifiers, used by Alembic.
revision = 'e9d2cec81d58'
down_revision = '9fdde5131a0f'
branch_labels = None
depends_on = None


def upgrade():
    vectorizer.clear()

    conn = op.get_bind()
    sync_trigger(conn, "knowledge_items", "search_vector", ["value"], options={
        'regconfig': 'pg_catalog.simple'
    })

    op.execute("UPDATE knowledge_items SET value=value;")


def downgrade():
    pass
