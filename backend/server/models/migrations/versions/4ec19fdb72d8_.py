"""Populate subjects

Revision ID: 4ec19fdb72d8
Revises: 2aafaa8da1be
Create Date: 2021-04-24 11:36:54.050474

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4ec19fdb72d8'
down_revision = '2aafaa8da1be'
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
