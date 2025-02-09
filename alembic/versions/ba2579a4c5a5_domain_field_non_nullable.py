"""domain field non nullable

Revision ID: ba2579a4c5a5
Revises: 00faae4a0e43
Create Date: 2020-06-01 09:16:35.061811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba2579a4c5a5'
down_revision = '00faae4a0e43'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'domains', ['domain'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'domains', type_='unique')
    # ### end Alembic commands ###
