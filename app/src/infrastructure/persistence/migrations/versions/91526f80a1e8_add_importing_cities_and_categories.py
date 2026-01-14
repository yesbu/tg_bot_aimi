"""add importing cities and categories

Revision ID: 91526f80a1e8
Revises: ec98ab604b60
Create Date: 2026-01-15 02:59:48.177826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '91526f80a1e8'
down_revision: Union[str, Sequence[str], None] = 'ec98ab604b60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    conn.execute(sa.text("INSERT INTO countries (id, code) VALUES (1, 'KZ')"))
    
    conn.execute(sa.text("INSERT INTO languages (id, code, name, is_default) VALUES (1, 'ru', 'Русский', true)"))

    
    cities_data = [
        (1, 1, 'Алматы'),
        (2, 1, 'Астана'),
        (3, 1, 'Шымкент'),
        (4, 1, 'Актау'),
        (5, 1, 'Актобе'),
        (6, 1, 'Атырау'),
        (7, 1, 'Караганда'),
        (8, 1, 'Костанай'),
        (9, 1, 'Кызылорда'),
        (10, 1, 'Павлодар'),
        (11, 1, 'Петропавловск'),
        (12, 1, 'Тараз'),
        (13, 1, 'Уральск'),
        (14, 1, 'Усть-Каменогорск'),
    ]
    
    for city_id, country_id, city_name in cities_data:
        conn.execute(sa.text(
            f"INSERT INTO cities (id, country_id) VALUES ({city_id}, {country_id})"
        ))
        conn.execute(sa.text(
            f"INSERT INTO city_translations (city_id, language_id, name) "
            f"VALUES ({city_id}, 1, '{city_name}')"
        ))
    
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
    conn.execute(sa.text("DELETE FROM city_translations"))
    conn.execute(sa.text("DELETE FROM cities"))
    conn.execute(sa.text("DELETE FROM languages"))
    conn.execute(sa.text("DELETE FROM countries"))
