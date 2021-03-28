""" Fix admin password set by e24bb0f4ef36

Revision ID: 4dd249699117
Revises: 22298efedbdd
Create Date: 2020-11-08 21:15:58.073510

"""
import sqlalchemy as sa
from alembic import op
from flask_bcrypt import generate_password_hash as gph
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = '4dd249699117'
down_revision = '22298efedbdd'
branch_labels = None
depends_on = None


def upgrade():
    password = gph("Asdfgh12!", 12)
    admin_table = sa.Table("admin", sa.MetaData(
        bind=op.get_bind()), autoload=True)

    op.execute(
        admin_table.update()
                   .where(admin_table.c.email == 'default_admin@zenteach.co.uk')
                   .values(password=password)
    )


def downgrade():
    # Revert to old encryption
    password = generate_password_hash("Asdfgh12!")
    admin_table = sa.Table("admin", sa.MetaData(
        bind=op.get_bind()), autoload=True)

    op.execute(
        admin_table.update()
        .where(admin_table.c.email == 'default_admin@zenteach.co.uk')
        .values(password=password)
    )
