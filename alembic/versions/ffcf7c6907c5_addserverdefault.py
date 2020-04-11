# flake8: noqa
"""Add Server Default

Revision ID: ffcf7c6907c5
Revises: 2bd90d157593
Create Date: 2020-04-11 19:39:55.094675

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ffcf7c6907c5'
down_revision = '2bd90d157593'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('company', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('company', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('stockprice', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('stockprice', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('stockprice_ma', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('stockprice_ma', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('stockprice_ma', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('stockprice_ma', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('stockprice', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('stockprice', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('company', 'upd_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('company', 'ins_ts',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    # ### end Alembic commands ###