"""Add email to User

Revision ID: 19a2b5ccfddb
Revises: bad64bf96870
Create Date: 2025-05-07 11:42:37.653818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19a2b5ccfddb'
down_revision = 'bad64bf96870'
branch_labels = None
depends_on = None


def upgrade():
    # Tilføj 'email'-kolonnen som nullable for at undgå fejl på eksisterende rækker
    op.add_column(
        'user',
        sa.Column('email', sa.String(length=120), nullable=True)
    )
    # Opret unik constraint med eksplicit navn
    op.create_unique_constraint(
        'uq_user_email',
        'user',
        ['email']
    )


def downgrade():
    # Fjern den unikke constraint først
    op.drop_constraint('uq_user_email', 'user', type_='unique')
    # Fjern kolonnen igen
    op.drop_column('user', 'email')
