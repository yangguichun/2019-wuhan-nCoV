"""empty message

Revision ID: 31da0ed98eba
Revises: 14548a7b78d0
Create Date: 2020-01-29 17:24:06.052225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31da0ed98eba'
down_revision = '14548a7b78d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('statistic_data', 'areaType')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('statistic_data', sa.Column('areaType', sa.TEXT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###