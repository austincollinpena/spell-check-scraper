"""Initial Migration

Revision ID: 00faae4a0e43
Revises: 
Create Date: 2020-06-01 08:59:53.066514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00faae4a0e43'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('domains',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('page', sa.String(), nullable=False),
    sa.Column('errors', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('domain', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['domain'], ['domains.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pages')
    op.drop_table('domains')
    # ### end Alembic commands ###
