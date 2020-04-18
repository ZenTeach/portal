"""Update ClassQuizStatus enum

Revision ID: 1cab4acb0223
Revises: 36e109d3994e
Create Date: 2020-04-03 19:42:11.377727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cab4acb0223'
down_revision = '36e109d3994e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('COMMIT;')
    op.execute("ALTER TYPE classquizstatus ADD VALUE 'in_progress' AFTER 'created';")
    op.execute("ALTER TYPE classquizstatus ADD VALUE 'graded' AFTER 'administered';")


def downgrade():
    op.execute("""
        DROP TYPE classquizstatus;
        CREATE TYPE classquizstatus AS ENUM  ('created', 'administered', 'cancelled');
    """)
