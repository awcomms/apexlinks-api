"""empty message

Revision ID: 99ed48965eae
Revises: f8a09358ea87
Create Date: 2022-07-05 19:29:00.355931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99ed48965eae'
down_revision = 'f8a09358ea87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('txt', sa.Column('search_tags', sa.JSON(), nullable=True))
    op.drop_column('txt', 'seen')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('txt', sa.Column('seen', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('txt', 'search_tags')
    # ### end Alembic commands ###