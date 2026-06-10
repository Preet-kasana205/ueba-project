"""fix is_current column type in baselines

Revision ID: c498be91017e
Revises: c0ae36a862fe
Create Date: 2026-06-10 09:15:43.937856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c498be91017e'
down_revision: Union[str, Sequence[str], None] = 'c0ae36a862fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE baselines 
        ALTER COLUMN is_current TYPE BOOLEAN 
        USING is_current::boolean
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE baselines 
        ALTER COLUMN is_current TYPE VARCHAR 
        USING is_current::varchar
    """)