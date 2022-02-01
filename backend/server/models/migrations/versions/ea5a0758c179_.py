"""Add Activity Log

Revision ID: ea5a0758c179
Revises: c7fc56d7ee51
Create Date: 2022-02-01 22:17:57.515140

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ea5a0758c179'
down_revision = 'c7fc56d7ee51'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('activity_log',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('actor_id', sa.Integer(), nullable=False),
                    sa.Column('action', sa.String(length=128), nullable=False),
                    sa.Column('item_type', sa.String(length=128), nullable=False),
                    sa.Column('item_id', sa.Integer(), nullable=False),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('created', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(['actor_id'], ['teacher.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('activity_log')
