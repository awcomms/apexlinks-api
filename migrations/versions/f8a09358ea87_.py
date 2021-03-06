"""empty message

Revision ID: f8a09358ea87
Revises: b11f4ff2ce57
Create Date: 2022-06-30 09:57:10.667004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8a09358ea87'
down_revision = 'b11f4ff2ce57'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('txt', sa.Column('text', sa.Unicode(), nullable=True))
    op.drop_column('txt', 'about')
    op.add_column('user', sa.Column('text', sa.Unicode(), nullable=True))
    op.drop_column('user', 'about')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('user', 'text')
    op.add_column('txt', sa.Column('about', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('txt', 'text')
    # ### end Alembic commands ###
