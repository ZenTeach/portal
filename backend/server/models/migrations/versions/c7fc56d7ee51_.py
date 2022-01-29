"""Add timestamp to base model objects

Revision ID: c7fc56d7ee51
Revises: 6520f6dc2dc9
Create Date: 2022-01-28 23:22:33.946550

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.expression import text

# revision identifiers, used by Alembic.
revision = 'c7fc56d7ee51'
down_revision = '6520f6dc2dc9'
branch_labels = None
depends_on = None


def upgrade():
    tables = ['admin', 'class_quiz', 'invitations',
              'knowledge_items', 'question_choice', 'questions',
              'quiz_grade', 'quiz_session', 'school_class',
              'student', 'student_attended_class', 'subjects',
              'teacher', 'topics']
    for table in tables:
        op.add_column(table, sa.Column('created', sa.DateTime(),
                                       nullable=True, server_default=text('CURRENT_TIMESTAMP')))
        op.add_column(table, sa.Column('updated', sa.DateTime(),
                                       nullable=True, server_default=text('CURRENT_TIMESTAMP')))
        op.execute(f"UPDATE {table} SET created = CURRENT_TIMESTAMP;")
        op.execute(f"UPDATE {table} SET updated = CURRENT_TIMESTAMP;")
        op.alter_column(table, 'created', nullable=False)
        op.alter_column(table, 'updated', nullable=False)


def downgrade():
    tables = ['admin', 'class_quiz', 'invitations',
              'knowledge_items', 'question_choice', 'questions',
              'quiz_grade', 'quiz_session', 'school_class',
              'student', 'student_attended_class', 'subjects',
              'teacher', 'topics']
    for table in tables:
        op.drop_column(table, 'created')
        op.drop_column(table, 'updated')
