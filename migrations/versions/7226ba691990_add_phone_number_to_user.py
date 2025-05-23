"""Add phone_number to user

Revision ID: 7226ba691990
Revises: ccb64432e4bf
Create Date: 2025-05-20 12:34:14.549024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7226ba691990'
down_revision = 'ccb64432e4bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('phone_number')

    # ### end Alembic commands ###
