"""empty message

Revision ID: 71382e6455de
Revises: 86acbdbda56c
Create Date: 2021-10-18 05:56:59.121025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71382e6455de'
down_revision = '86acbdbda56c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('site_page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=True),
    sa.Column('lastmod', sa.DateTime(), nullable=True),
    sa.Column('changefreq', sa.Unicode(), nullable=True),
    sa.Column('disallow', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sitemap_index',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lastmod', sa.DateTime(), nullable=True),
    sa.Column('loc', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sitemap',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('index_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['index_id'], ['sitemap_index.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('lastmod', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('sitemap_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'sitemap', ['sitemap_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'sitemap_id')
    op.drop_column('user', 'lastmod')
    op.drop_table('sitemap')
    op.drop_table('sitemap_index')
    op.drop_table('site_page')
    # ### end Alembic commands ###
