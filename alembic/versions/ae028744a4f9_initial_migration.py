"""Initial migration

Revision ID: ae028744a4f9
Revises: b18d1ddb6c6f
Create Date: 2024-06-23 07:06:09.977884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae028744a4f9'
down_revision: Union[str, None] = 'b18d1ddb6c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('sex', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'sex')
    # ### end Alembic commands ###
