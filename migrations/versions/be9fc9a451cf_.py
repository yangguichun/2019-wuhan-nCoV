"""empty message

Revision ID: be9fc9a451cf
Revises: 63989d2d500f
Create Date: 2020-02-03 18:18:30.004832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be9fc9a451cf'
down_revision = '63989d2d500f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api_log', sa.Column('api', sa.Text(), nullable=True))
    op.add_column('api_log', sa.Column('params', sa.Text(), nullable=True))
    op.drop_column('api_log', 'path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api_log', sa.Column('path', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('api_log', 'params')
    op.drop_column('api_log', 'api')
    # ### end Alembic commands ###