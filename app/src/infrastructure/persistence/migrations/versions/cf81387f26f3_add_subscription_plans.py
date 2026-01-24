"""add subscription plans

Revision ID: cf81387f26f3
Revises: 2ba7b19cf41f
Create Date: 2026-01-24 00:35:56.328195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf81387f26f3'
down_revision: Union[str, Sequence[str], None] = '2ba7b19cf41f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    plans_data = [
        (
            1,
            'BASIC',
            3,
            195000.0,
            20,
            '• доступ к базовым детским центрам сети\n• стандартное бронирование',
            True,
            1
        ),
        (
            2,
            'SMART',
            6,
            300000.0,
            30,
            '• доступ к расширенной сети детских центров\n• приоритетное бронирование\n• возможность переноса посещений',
            True,
            2
        ),
        (
            3,
            'PRO',
            12,
            516000.0,
            40,
            '• доступ ко всем детским центрам сети\n• приоритетное бронирование\n• перенос и заморозка посещений',
            True,
            3
        ),
    ]
    
    for plan_id, name, duration, price, visits, description, is_active, display_order in plans_data:
        conn.execute(sa.text(
            f"INSERT INTO subscription_plans "
            f"(id, name, duration_months, price, visits_limit, description, is_active, display_order) "
            f"VALUES ({plan_id}, '{name}', {duration}, {price}, {visits}, "
            f"'{description}', {is_active}, {display_order})"
        ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM subscription_plans WHERE id IN (1, 2, 3)"))
