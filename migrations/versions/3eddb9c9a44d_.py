"""empty message

Revision ID: 3eddb9c9a44d
Revises: 75e78de4b9cc
Create Date: 2021-03-31 11:33:06.917217

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3eddb9c9a44d'
down_revision = '75e78de4b9cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('address', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('email', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('name', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('phone', sa.Unicode(), nullable=True))
    op.add_column('user', sa.Column('website', sa.Unicode(), nullable=True))
    op.drop_column('user', 'online')
    op.drop_column('user', 'in_rooms')
    op.drop_column('user', 'unseen_rooms')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('unseen_rooms', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('in_rooms', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('online', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('user', 'website')
    op.drop_column('user', 'phone')
    op.drop_column('user', 'name')
    op.drop_column('user', 'email')
    op.drop_column('user', 'address')
    # ### end Alembic commands ###