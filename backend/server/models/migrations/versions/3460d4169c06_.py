"""Add unique constraints on student and teacher

Revision ID: 3460d4169c06
Revises: a7e63a4fafa3
Create Date: 2020-03-29 17:49:04.283379

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "3460d4169c06"
down_revision = "a7e63a4fafa3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_teacher_email", "teacher", ["email"])
    op.create_unique_constraint("uq_student_email", "student", ["email"])
    op.create_unique_constraint("uq_admin_email", "admin", ["email"])


def downgrade():
    op.drop_constraint("uq_teacher_email")
    op.drop_constraint("uq_student_email")
    op.drop_constraint("uq_admin_email")
