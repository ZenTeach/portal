"""Sync and update search vectors for topics

Revision ID: bb1ac1a0f214
Revises: a740b0a8db46
Create Date: 2021-09-11 08:59:13.850500

"""
from alembic import op
from sqlalchemy_searchable import sync_trigger, vectorizer

# revision identifiers, used by Alembic.
revision = 'bb1ac1a0f214'
down_revision = 'a740b0a8db46'
branch_labels = None
depends_on = None


def upgrade():
    vectorizer.clear()

    conn = op.get_bind()
    sync_trigger(conn, "topics", "search_vector", ["value"], options={
        'regconfig': 'pg_catalog.simple'
    })

    op.execute("UPDATE topics SET value=value;")


def downgrade():
    pass
