"""empty message

Revision ID: b0562afca0df
Revises: acbe2c2a954a
Create Date: 2021-03-14 11:48:13.245847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0562afca0df'
down_revision = 'acbe2c2a954a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group', sa.Column('users', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group', 'users')
    # ### end Alembic commands ###
