"""empty message

Revision ID: c2342ffd6af1
Revises: deaadf16923c
Create Date: 2022-01-07 23:54:18.584637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2342ffd6af1'
down_revision = 'deaadf16923c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('_saved_items', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('_saved_items', sa.Column('item_id', sa.Integer(), nullable=True))
    op.add_column('_saved_items', sa.Column('tags', sa.JSON(), nullable=True))
    op.drop_constraint('_saved_items_user_fkey', '_saved_items', type_='foreignkey')
    op.drop_constraint('_saved_items_item_fkey', '_saved_items', type_='foreignkey')
    op.create_foreign_key(None, '_saved_items', 'item', ['item_id'], ['id'])
    op.create_foreign_key(None, '_saved_items', 'user', ['user_id'], ['id'])
    op.drop_column('_saved_items', 'item')
    op.drop_column('_saved_items', 'user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('_saved_items', sa.Column('user', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('_saved_items', sa.Column('item', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, '_saved_items', type_='foreignkey')
    op.drop_constraint(None, '_saved_items', type_='foreignkey')
    op.create_foreign_key('_saved_items_item_fkey', '_saved_items', 'item', ['item'], ['id'])
    op.create_foreign_key('_saved_items_user_fkey', '_saved_items', 'user', ['user'], ['id'])
    op.drop_column('_saved_items', 'tags')
    op.drop_column('_saved_items', 'item_id')
    op.drop_column('_saved_items', 'user_id')
    # ### end Alembic commands ###
