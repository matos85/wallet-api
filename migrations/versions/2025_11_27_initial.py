"""initial

Revision ID: abc123
Revises:
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'wallets',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('balance', sa.Integer, default=0)
    )

def downgrade():
    op.drop_table('wallets')