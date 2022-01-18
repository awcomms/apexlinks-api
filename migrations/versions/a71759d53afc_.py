"""empty message

Revision ID: a71759d53afc
Revises: f951bb2016a4
Create Date: 2022-01-14 17:10:22.685694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a71759d53afc'
down_revision = 'f951bb2016a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('settings', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'settings')
    # ### end Alembic commands ###