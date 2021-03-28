"""Create a default admin user

Revision ID: e24bb0f4ef36
Revises: 3460d4169c06
Create Date: 2020-03-29 19:01:44.592481

"""
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = "e24bb0f4ef36"
down_revision = "3460d4169c06"
branch_labels = None
depends_on = None


def upgrade():
    password = generate_password_hash("Asdfgh12!")
    admin_table = sa.Table("admin", sa.MetaData(
        bind=op.get_bind()), autoload=True)
    op.execute(
        admin_table.insert().values(
            firstname="Zenteach",
            lastname="Admin",
            email="default_admin@zenteach.co.uk",
            date_of_birth="04-04-1975",
            password=password,
            role="Admin",
            uuid=str(uuid4()),
        )
    )


def downgrade():
    default_admin_user = "default_admin@zenteach.co.uk"
    op.execute("DELETE FROM admin WHERE email='{}'".format(default_admin_user))  # nosec
