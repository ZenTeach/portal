"""Rename topics and knowledge items columns in questions

Revision ID: 959128049016
Revises: bdd21edb3007
Create Date: 2021-09-24 11:48:07.836942

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '959128049016'
down_revision = 'bdd21edb3007'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE questions
        RENAME COLUMN _topic_id TO topic_id
    """)

    op.execute("""
        ALTER TABLE questions
        RENAME COLUMN _knowledge_item_id TO knowledge_item_id
    """)
