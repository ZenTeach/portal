"""Add unique constraints on questions and school_class tables

Revision ID: cad140b11e16
Revises: 32d92a8d0523
Create Date: 2019-10-30 10:57:25.039642

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "cad140b11e16"
down_revision = "32d92a8d0523"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_question_subject_topic_knowledge_item_question_type",
        "questions",
        ["question", "subject", "topic", "knowledge_item", "question_type"],
    )
    op.create_unique_constraint(
        "uq_class_name_subject_teacher_id",
        "school_class",
        ["name", "subject", "teacher_id"],
    )


def downgrade():
    op.drop_constraint(
        "uq_question_subject_topic_knowledge_item_question_type")
    op.drop_constraint("uq_class_name_subject_teacher_id")
