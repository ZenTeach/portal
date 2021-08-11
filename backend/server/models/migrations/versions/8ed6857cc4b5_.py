"""Rename topic to topics

Revision ID: 8ed6857cc4b5
Revises: e907e2b0bbab
Create Date: 2021-08-07 15:07:35.324681

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '8ed6857cc4b5'
down_revision = '4b6fb0f4c30c'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("ALTER TABLE IF EXISTS topic RENAME TO topics")


def downgrade():
    connection = op.get_bind()
    connection.execute("ALTER TABLE IF EXISTS topics RENAME TO topic")
