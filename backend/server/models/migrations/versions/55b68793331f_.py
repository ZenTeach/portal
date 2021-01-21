"""Use Simple catalog in questions_search_vector_update function

Revision ID: 55b68793331f
Revises: 29716a6f67a0
Create Date: 2021-01-20 21:38:23.285910

"""
from alembic import op
from sqlalchemy_searchable import sync_trigger, vectorizer

# revision identifiers, used by Alembic.
revision = '55b68793331f'
down_revision = '29716a6f67a0'
branch_labels = None
depends_on = None


def upgrade():
    # Update vectorizer sync
    vectorizer.clear()

    conn = op.get_bind()
    sync_trigger(conn, "questions", "search_vector", ["question"], options={
        'regconfig': 'pg_catalog.simple'
    })

    op.execute("UPDATE questions SET question=question;")


def downgrade():
    vectorizer.clear()

    conn = op.get_bind()
    sync_trigger(conn, "questions", "search_vector", ["question"])

    op.execute("UPDATE questions SET question=question;")
