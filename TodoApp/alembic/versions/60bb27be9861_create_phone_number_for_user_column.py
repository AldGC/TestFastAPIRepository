"""Create Phone number for user column

Revision ID: 60bb27be9861
Revises: 
Create Date: 2023-09-30 17:07:07.556807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60bb27be9861'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'phone_number')
