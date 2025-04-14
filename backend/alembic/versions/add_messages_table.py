"""Add messages table

Revision ID: add_messages_table
Revises: update_vector_dimension
Create Date: 2024-04-15 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_messages_table'
down_revision: Union[str, None] = 'update_vector_dimension'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create sequence for message_id
    op.execute('CREATE SEQUENCE message_id_seq START 1')
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('message_id', sa.Integer(), sa.Sequence('message_id_seq'), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('message_id')
    )
    
    # Create indices for faster lookups
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.create_index('ix_messages_recipient_id', 'messages', ['recipient_id'], unique=False)
    op.create_index('ix_messages_timestamp', 'messages', ['timestamp'], unique=False)
    
    # Create a composite index for conversation lookup
    op.create_index(
        'ix_messages_conversation',
        'messages',
        ['sender_id', 'recipient_id', 'timestamp'],
        unique=False
    )

def downgrade() -> None:
    # Drop messages table
    op.drop_table('messages')
    
    # Drop sequence
    op.execute('DROP SEQUENCE IF EXISTS message_id_seq') 