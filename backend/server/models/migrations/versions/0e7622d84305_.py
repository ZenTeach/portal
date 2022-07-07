"""Drop unique index on activity log (uniq_action_item_type_item_id)

Revision ID: 0e7622d84305
Revises: d428c7b930ea
Create Date: 2022-07-05 20:38:50.993132

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0e7622d84305'
down_revision = 'd428c7b930ea'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE activity_log DROP CONSTRAINT IF EXISTS uniq_action_item_type_item_id")


def downgrade():
    op.execute("CREATE UNIQUE INDEX uniq_action_item_type_item_id ON activity_log(action,item_type,item_id)")  # noqa
