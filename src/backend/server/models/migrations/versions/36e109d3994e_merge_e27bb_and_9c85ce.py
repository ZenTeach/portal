"""merge migrations for e27bb and 9c85ce

Revision ID: 36e109d3994e
Revises: e24bb0f4ef36, 9c85ceb994ae
Create Date: 2020-04-02 14:33:19.128593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36e109d3994e'
down_revision = ('e24bb0f4ef36', '9c85ceb994ae')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
