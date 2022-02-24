"""Add a quiz session primary key

Revision ID: 410b3bf0b1dd
Revises: ea5a0758c179
Create Date: 2022-02-24 21:19:06.249881

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '410b3bf0b1dd'
down_revision = 'ea5a0758c179'
branch_labels = None
depends_on = None


def upgrade():
    op.create_primary_key('quiz_session_pkey', 'quiz_session', ['uuid'])


def downgrade():
    op.drop_constraint('quiz_session_pkey', 'quiz_session', type_='primary')
