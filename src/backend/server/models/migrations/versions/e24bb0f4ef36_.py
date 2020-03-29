"""Create a default admin user

Revision ID: e24bb0f4ef36
Revises: 3460d4169c06
Create Date: 2020-03-29 19:01:44.592481

"""
from alembic import op
import sqlalchemy as sa
from server.models import Admin
from server import bcrypt, db
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = 'e24bb0f4ef36'
down_revision = '3460d4169c06'
branch_labels = None
depends_on = None


def upgrade():
    password = bcrypt.generate_password_hash('Asdfgh12!')
    Admin(firstname="Zenteach", lastname="Admin", email="default_admin@zenteach.co.uk", date_of_birth="04-04-1975",
            password=password.decode('utf-8'), role="Admin", uuid=uuid4()).save()


def downgrade():
   a = Admin.query.filter_by(email="default_admin@zenteach.co.uk").first()
   db.session.delete(a)
   db.session.commit()
