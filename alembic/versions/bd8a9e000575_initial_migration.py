"""Initial migration

Revision ID: bd8a9e000575
Revises: 8283fa5a5e51
Create Date: 2024-06-04 18:29:29.850379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'bd8a9e000575'
down_revision: Union[str, None] = '8283fa5a5e51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('share_signature')
    op.drop_table('user_posts')
    op.drop_table('user_history')
    op.drop_table('signature')
    op.add_column('account', sa.Column('emailStatus', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('account', 'emailStatus')
    op.create_table('signature',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('signature', mysql.VARCHAR(length=25), nullable=False),
    sa.Column('create_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('update_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('isDeleted', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], name='signature_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user_history',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('url', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('isDeleted', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('create_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('last_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], name='user_history_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user_posts',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('content', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('create_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('status', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('update_time', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('isDisabledTitle', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('isDeleted', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('isTop', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], name='user_posts_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('share_signature',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('type', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('share_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('count', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['share_id'], ['user_posts.id'], name='share_signature_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], name='share_signature_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
