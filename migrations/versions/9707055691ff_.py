"""empty message

Revision ID: 9707055691ff
Revises: 597e0df562f3
Create Date: 2022-07-10 20:40:39.837139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9707055691ff'
down_revision = '597e0df562f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('txt', sa.Column('anon', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('txt', 'anon')
    # ### end Alembic commands ###
