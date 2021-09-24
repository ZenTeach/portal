"""Add Psychology subject

Revision ID: bdd21edb3007
Revises: 49c2d0f39a77
Create Date: 2021-09-24 11:29:50.115992

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bdd21edb3007'
down_revision = '49c2d0f39a77'
branch_labels = None
depends_on = None


def upgrade():
    subjects_table = sa.Table('subjects', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    op.execute(
        subjects_table.insert().values(name='Psychology', enabled=False, remark="")
    )


def downgrade():
    op.execute("DELETE FROM subjects WHERE name='Psychology'")
