"""SchoolClass keystage migration

Revision ID: 1575b17e8760
Revises: 2028279d7185
Create Date: 2021-06-11 17:50:11.197399

"""
from server.models import SchoolClass

# revision identifiers, used by Alembic.
revision = '1575b17e8760'
down_revision = '2028279d7185'
branch_labels = None
depends_on = None


def upgrade():
    for _class in SchoolClass.query.filter(SchoolClass.year_group != None).all():  # noqa
        _class.key_stage = _class.key_stage_from_year_group(_class.year_group)
        _class.save()


def downgrade():
    pass
