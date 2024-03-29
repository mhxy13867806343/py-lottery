"""Your add db

Revision ID: 2d105fde9194
Revises: 143e55a33961
Create Date: 2024-03-25 15:13:26.356555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d105fde9194'
down_revision: Union[str, None] = '143e55a33961'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email', sa.Column('status', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('email', 'status')
    # ### end Alembic commands ###
