"""add categories

Revision ID: 2ba7b19cf41f
Revises: 2d19caff90c0
Create Date: 2026-01-24 00:34:30.210160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ba7b19cf41f'
down_revision: Union[str, Sequence[str], None] = '2d19caff90c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    categories_data = [
        (1, 'languages', 'Языки'),
        (2, 'it', 'IT'),
        (3, 'music', 'Музыка'),
        (4, 'math', 'Математика'),
        (5, 'ent', 'ЕНТ'),
        (6, 'art', 'Искусство'),
        (7, 'sport', 'Спорт'),
        (8, 'other', 'Другое'),
    ]
    
    for cat_id, code, name in categories_data:
        conn.execute(sa.text(
            f"INSERT INTO course_categories (id, code, is_active) "
            f"VALUES ({cat_id}, '{code}', true)"
        ))
        conn.execute(sa.text(
            f"INSERT INTO course_category_translations (category_id, language_id, name) "
            f"VALUES ({cat_id}, 1, '{name}')"
        ))



def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DELETE FROM course_category_translations"))
    conn.execute(sa.text("DELETE FROM course_categories"))
    