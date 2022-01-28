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
    op.add_column('admin', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('admin', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('class_quiz', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('class_quiz', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('invitations', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('invitations', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('knowledge_items', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('knowledge_items', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('question_choice', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('question_choice', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('questions', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('questions', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('quiz_grade', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('quiz_grade', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('quiz_session', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('quiz_session', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('school_class', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('school_class', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('student', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('student', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('student_attended_class', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('student_attended_class', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('subjects', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('subjects', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('teacher', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('teacher', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('topics', sa.Column('created', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))
    op.add_column('topics', sa.Column('updated', sa.DateTime(),
                  nullable=True, server_default=text('CURRENT_TIMESTAMP')))


def downgrade():
    op.drop_column('topics', 'updated')
    op.drop_column('topics', 'created')
    op.drop_column('teacher', 'updated')
    op.drop_column('teacher', 'created')
    op.drop_column('subjects', 'updated')
    op.drop_column('subjects', 'created')
    op.drop_column('student_attended_class', 'updated')
    op.drop_column('student_attended_class', 'created')
    op.drop_column('student', 'updated')
    op.drop_column('student', 'created')
    op.drop_column('school_class', 'updated')
    op.drop_column('school_class', 'created')
    op.drop_column('quiz_session', 'updated')
    op.drop_column('quiz_session', 'created')
    op.drop_column('quiz_grade', 'updated')
    op.drop_column('quiz_grade', 'created')
    op.drop_column('questions', 'updated')
    op.drop_column('questions', 'created')
    op.drop_column('question_choice', 'updated')
    op.drop_column('question_choice', 'created')
    op.drop_column('knowledge_items', 'updated')
    op.drop_column('knowledge_items', 'created')
    op.drop_column('invitations', 'updated')
    op.drop_column('invitations', 'created')
    op.drop_column('class_quiz', 'updated')
    op.drop_column('class_quiz', 'created')
    op.drop_column('admin', 'updated')
    op.drop_column('admin', 'created')
