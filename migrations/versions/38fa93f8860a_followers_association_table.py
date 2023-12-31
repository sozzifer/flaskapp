"""followers association table

Revision ID: 38fa93f8860a
Revises: c0a848362bf5
Create Date: 2023-09-04 12:44:47.344983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38fa93f8860a'
down_revision = 'c0a848362bf5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
