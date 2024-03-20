"""Initial migration

Revision ID: 5992a6e608fd
Revises: 4eb358969317
Create Date: 2024-03-20 10:09:37.259573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5992a6e608fd'
down_revision: Union[str, None] = '4eb358969317'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('status', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'status')
    # ### end Alembic commands ###
