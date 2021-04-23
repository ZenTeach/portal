"""Add subject_id on questions

Revision ID: 389b937b1b53
Revises: ff484a08dfe1
Create Date: 2021-04-23 18:58:20.938340

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '389b937b1b53'
down_revision = 'ff484a08dfe1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('questions', sa.Column('subject_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('questions', 'subject_id')
