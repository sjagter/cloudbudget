"""transactions table

Revision ID: 5b65fca811f0
Revises: cbc9ea1a2862
Create Date: 2019-12-15 20:52:48.189266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b65fca811f0'
down_revision = 'cbc9ea1a2862'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('account_holder', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transaction', 'account_holder')
    # ### end Alembic commands ###
