"""empty message

Revision ID: 8f0769743ecb
Revises: b0562afca0df
Create Date: 2021-03-15 10:48:11.810120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f0769743ecb'
down_revision = 'b0562afca0df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('saved_groups')
    op.drop_table('saved_users')
    op.add_column('user', sa.Column('socketId', sa.Unicode(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'socketId')
    op.create_table('saved_users',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='saved_users_user_id_fkey')
    )
    op.create_table('saved_groups',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('group', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['group'], ['group.id'], name='saved_groups_group_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='saved_groups_user_id_fkey')
    )
    # ### end Alembic commands ###
