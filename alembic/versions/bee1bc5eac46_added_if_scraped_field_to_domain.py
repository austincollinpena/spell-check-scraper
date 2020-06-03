"""added if scraped field to domain

Revision ID: bee1bc5eac46
Revises: eb43f807e48d
Create Date: 2020-06-03 12:10:55.267362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bee1bc5eac46'
down_revision = 'eb43f807e48d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('domains', sa.Column('is_scraped', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('domains', 'is_scraped')
    # ### end Alembic commands ###
