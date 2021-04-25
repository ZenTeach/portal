"""Migrate data from questions.subject to questions.subject_id

Revision ID: 009655ab4286
Revises: 389b937b1b53
Create Date: 2021-04-23 19:00:33.181236

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision = '009655ab4286'
down_revision = '389b937b1b53'
branch_labels = None
depends_on = None


def upgrade():

    session = sessionmaker(bind=op.get_bind().engine)()
    select_sql = """
        select questions.id, subjects.id as subject_id
        from questions
        inner join subjects
        on subjects.name = questions.subject;
    """

    # Tuple of questions.id and subjects.id
    results = session.execute(select_sql).fetchall()
    session.close()

    questions_table = sa.Table('questions', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    for result in results:
        update_stmt = sa.update(questions_table).where(
            questions_table.c.id == result[0]
        ).values(
            subject_id=result[1]
        )
        op.execute(update_stmt)

    op.create_foreign_key(None, 'questions', 'subjects', ['subject_id'], ['id'])
    op.drop_column('questions', 'subject')


def downgrade():
    op.add_column('questions', sa.Column('subject', sa.VARCHAR(
        length=256), autoincrement=False, nullable=False))
    session = sessionmaker(bind=op.get_bind().engine)()
    questions_table = sa.Table('questions', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    select_sql = """
        select questions.id, subjects.name
        from questions
        inner join subjects
        on subjects.id = questions.subject_id;
    """
    results = session.execute(select_sql).fetchall()

    for result in results:
        update_stmt = sa.update(questions_table).where(
            questions_table.c.id == result[0]
        ).values(
            subject=result[1]
        )
        session.execute(update_stmt)

    op.drop_constraint(None, 'questions', type_='foreignkey')
    op.drop_column('questions', 'subject_id')
