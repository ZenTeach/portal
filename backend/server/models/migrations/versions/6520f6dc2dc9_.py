"""Add invitee on invitation model

Revision ID: 6520f6dc2dc9
Revises: b5ed2dccb3fc
Create Date: 2021-12-23 14:42:14.843738

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6520f6dc2dc9'
down_revision = 'b5ed2dccb3fc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('invitations', sa.Column('invitee_id', sa.Integer(), nullable=True))
    op.create_foreign_key('invitations_invitee_id_fkey', 'invitations',
                          'teacher', ['invitee_id'], ['id'])


def downgrade():
    op.drop_constraint('invitations_invitee_id_fkey', 'invitations', type_='foreignkey')
    op.drop_column('invitations', 'invitee_id')
