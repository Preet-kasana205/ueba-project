"""add checksum index to raw events

Revision ID: d138a2b0144d
Revises: ef1d7e80fe42
Create Date: 2026-06-06 08:22:27.465286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd138a2b0144d'
down_revision: Union[str, Sequence[str], None] = 'ef1d7e80fe42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ix_raw_events_checksum',
        'raw_events',
        ['checksum'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_raw_events_checksum', table_name='raw_events')


