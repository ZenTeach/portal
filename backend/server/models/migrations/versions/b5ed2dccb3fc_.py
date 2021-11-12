"""Data migration: set user created choices

Revision ID: b5ed2dccb3fc
Revises: 6d6e14d5d0b6
Create Date: 2021-11-12 23:12:19.350049

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b5ed2dccb3fc'
down_revision = '6d6e14d5d0b6'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    choice_teacher_id_tuple_sql = sa.text(
        'SELECT choice.id, q.teacher_id FROM question_choice choice INNER JOIN questions \
        q ON choice.question_id = q.id WHERE q.user_created=true AND q.teacher_id IS NOT NULL AND \
        choice.user_created IS NULL AND choice.teacher_id IS NULL;'
    )
    sql_result = connection.execute(choice_teacher_id_tuple_sql)
    choice_teacher_id_tuple = sql_result.fetchall()

    choice_update_sql = sa.text(
        'UPDATE question_choice SET teacher_id=:teacher_id, user_created=true \
        WHERE id = :choice_id;'
    )
    choice_update_sql = choice_update_sql.bindparams(
        sa.bindparam('teacher_id'), sa.bindparam('choice_id'))

    for choice_teacher_id in choice_teacher_id_tuple:
        connection.execute(
            choice_update_sql,
            choice_id=(choice_teacher_id[0]),
            teacher_id=(choice_teacher_id[1])
        )


def downgrade():
    pass
