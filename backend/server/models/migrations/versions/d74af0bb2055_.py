"""Data migration: Backfill users table from teachers

Revision ID: d74af0bb2055
Revises: 33a9b88c44bb
Create Date: 2022-09-01 22:34:13.806289

"""
import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd74af0bb2055'
down_revision = '33a9b88c44bb'
branch_labels = None
depends_on = None


def upgrade():
    users_table = sa.Table('users',
                           sa.MetaData(bind=op.get_bind()),
                           autoload=True)
    teachers_count = op.execute("select count(*) from teacher;")
    if teachers_count is None:
        return

    if teachers_count.rowcount != 0:
        connection = op.get_bind()
        count = teachers_count.fetch_all()[0][0]
        for i in range(count):
            stmt = sa.insert(users_table).values(
                type='teacher', created=datetime.datetime.now(), updated=datetime.datetime.now())
            connection.execute(stmt)


def downgrade():
    op.execute('TRUNCATE TABLE users;')
