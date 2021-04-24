"""Migrate data to subject_id column on school_class

Revision ID: e7b39f502502
Revises: 91566f68862e
Create Date: 2021-04-24 17:31:07.428693

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision = 'e7b39f502502'
down_revision = '91566f68862e'
branch_labels = None
depends_on = None


def upgrade():
    school_class_table = sa.Table('school_class', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    session = sessionmaker(bind=op.get_bind().engine)()
    select_sql = """
        select school_class.id, subjects.id as subject_id
        from school_class
        inner join subjects
        on subjects.name = school_class.subject;
    """

    # Tuple of school_class.id and subjects.id
    results = session.execute(select_sql).fetchall()
    for result in results:
        update_stmt = sa.update(school_class_table).where(
            school_class_table.c.id == result[0]
        ).values(
            subject_id=result[1]
        )
        op.execute(update_stmt)
    session.close()

    op.create_foreign_key(None, 'school_class', 'subjects', ['subject_id'], ['id'])
    op.drop_column('school_class', 'subject')


def downgrade():
    op.add_column('school_class', sa.Column('subject', sa.VARCHAR(
        length=256), autoincrement=False, nullable=False))
    session = sessionmaker(bind=op.get_bind().engine)()
    school_class_table = sa.Table('school_class', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    select_sql = """
        select school_class.id, subjects.name
        from school_class
        inner join subjects
        on subjects.id = school_class.subject_id;
    """
    results = session.execute(select_sql).fetchall()

    for result in results:
        update_stmt = sa.update(school_class_table).where(
            school_class_table.c.id == result[0]
        ).values(
            subject=result[1]
        )
        session.execute(update_stmt)

    op.drop_constraint(None, 'school_class', type_='foreignkey')
    op.drop_column('school_class', 'subject_id')
