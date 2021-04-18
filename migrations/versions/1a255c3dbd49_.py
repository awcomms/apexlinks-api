"""empty message

Revision ID: 1a255c3dbd49
Revises: 3eddb9c9a44d
Create Date: 2021-04-18 10:26:06.756960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a255c3dbd49'
down_revision = '3eddb9c9a44d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('show_email', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'show_email')
    # ### end Alembic commands ###
