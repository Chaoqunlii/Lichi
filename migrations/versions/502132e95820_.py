"""empty message

Revision ID: 502132e95820
Revises: 8a0ce59c1d2d
Create Date: 2017-06-19 14:58:42.325876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '502132e95820'
down_revision = '8a0ce59c1d2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###