"""Migrate ChoiceFeedback to QuestionChoice column

Revision ID: f0f41c826502
Revises: a94357451f81
Create Date: 2020-07-21 07:41:43.112363

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import select

# revision identifiers, used by Alembic.
revision = 'f0f41c826502'
down_revision = 'a94357451f81'
branch_labels = None
depends_on = None


def upgrade():
    qc_table = sa.Table('question_choice', sa.MetaData(bind=op.get_bind()), autoload=True)
    cf_table = sa.Table('choice_feedback', sa.MetaData(bind=op.get_bind()), autoload=True)

    stmt = select([qc_table.c.id, cf_table.c.id, cf_table.c.content])\
        .select_from(qc_table.join(cf_table, qc_table.c.id == cf_table.c.choice_id))

    rows = op.get_bind().execute(stmt).fetchall()
    for row in rows:
        op.execute(
            "UPDATE question_choice SET feedback_text='{}'q WHERE id={}".format(row[2], row[0]))  # nosec # noqa


def downgrade():
    pass
