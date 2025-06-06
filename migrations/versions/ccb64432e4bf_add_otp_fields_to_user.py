"""Add OTP fields to user

Revision ID: ccb64432e4bf
Revises: 2bab3a10e8bc
Create Date: 2025-05-20 12:26:35.817957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccb64432e4bf'
down_revision = '2bab3a10e8bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('otp_code', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('otp_timestamp', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('otp_timestamp')
        batch_op.drop_column('otp_code')

    # ### end Alembic commands ###
