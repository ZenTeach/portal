"""Add activity log unique index


Revision ID: 47e86327063b
Revises: 410b3bf0b1dd
Create Date: 2022-05-17 22:22:53.519709

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '47e86327063b'
down_revision = '410b3bf0b1dd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        'uniq_action_item_type_item_id',
        'activity_log',
        ['action', 'item_type', 'item_id'],
        unique=True)


def downgrade():
    op.drop_index(
        'uniq_action_item_type_item_id',
        table_name='activity_log')
