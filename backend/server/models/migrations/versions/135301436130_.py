"""Populate subjects

Revision ID: 135301436130
Revises: 61be2397c781
Create Date: 2021-04-20 08:59:33.855278

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '135301436130'
down_revision = '61be2397c781'
branch_labels = None
depends_on = None


def upgrade():
    subjects = ["Art and Design",
                "Business",
                "Computer Science",
                "Design and Technology",
                "Drama",
                "English Language",
                "English Literature",
                "French",
                "Geography",
                "German",
                "History",
                "ICT",
                "Maths",
                "Media Studies",
                "Music",
                "Physical Education",
                "Religious Studies",
                "Sociology",
                "Spanish",
                "Biology",
                "Chemistry",
                "Physics"
                ]

    subjects_table = sa.Table('subjects', sa.MetaData(
        bind=op.get_bind()), autoload=True)

    for subject in subjects:
        op.execute(
            subjects_table.insert().values(name=subject, enabled=False, remark="")
        )

    op.alter_column('subjects', 'enabled', nullable=False)


def downgrade():
    op.alter_column('subjects', 'enabled', nullable=True)
    op.execute("TRUNCATE TABLE subjects;")
