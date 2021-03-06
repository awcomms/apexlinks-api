"""empty message

Revision ID: 0aefaa7f893a
Revises: e397bf84ab8a
Create Date: 2022-07-08 22:12:43.688496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0aefaa7f893a'
down_revision = 'e397bf84ab8a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('online', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'online')
    # ### end Alembic commands ###
