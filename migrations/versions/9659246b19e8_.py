"""empty message

Revision ID: 9659246b19e8
Revises: ac20563cd149
Create Date: 2022-06-27 12:22:30.586199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9659246b19e8'
down_revision = 'ac20563cd149'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('txt', sa.Column('tags', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('txt', 'tags')
    # ### end Alembic commands ###
