"""empty message

Revision ID: 29cf92d1a969
Revises: 3e604933c423
Create Date: 2014-09-18 10:13:01.346050

"""

# revision identifiers, used by Alembic.
revision = '29cf92d1a969'
down_revision = '3e604933c423'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('quantity_per_unit', sa.Integer(), nullable=True),
    sa.Column('max_available', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(length=255), nullable=True),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('item', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('user', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item'], ['item.id'], ),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order')
    op.drop_table('item')
    ### end Alembic commands ###
