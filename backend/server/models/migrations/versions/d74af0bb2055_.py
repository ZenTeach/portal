"""Data migration: Backfill users table from teachers

Revision ID: d74af0bb2055
Revises: 33a9b88c44bb
Create Date: 2022-09-01 22:34:13.806289

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision = 'd74af0bb2055'
down_revision = '33a9b88c44bb'
branch_labels = None
depends_on = None


def upgrade():
    session = sessionmaker(bind=op.get_bind().engine)()
    teachers_count = session.execute("select count(*) from teacher;").fetchall()

    users_table = sa.Table('users',
                           sa.MetaData(bind=op.get_bind()),
                           autoload=True)
    for i in range(teachers_count[0][0]):
        stmt = sa.insert(users_table).values(type='teacher')
        session.execute(stmt)

    session.close()


def downgrade():
    op.execute('TRUNCATE TABLE users;')
