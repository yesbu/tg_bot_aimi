import aiosqlite
import json
import logging
from datetime import datetime
from config import DATABASE_PATH, ROLE_USER, STATUS_PENDING

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Пользователи
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    role TEXT DEFAULT '{ROLE_USER}',
                    phone TEXT,
                    city TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Дети
            await db.execute("""
                CREATE TABLE IF NOT EXISTS children (
                    child_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_id INTEGER,
                    name TEXT NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES users(user_id)
                )
            """)

            # Образовательные центры
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS centers (
                    center_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partner_id INTEGER,
                    name TEXT NOT NULL,
                    city TEXT,
                    address TEXT,
                    phone TEXT,
                    category TEXT,
                    description TEXT,
                    logo TEXT,
                    status TEXT DEFAULT '{STATUS_PENDING}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partner_id) REFERENCES users(user_id)
                )
            """)

            # Преподаватели
            await db.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    center_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (center_id) REFERENCES centers(center_id)
                )
            """)

            # Курсы
            await db.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    center_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    age_min INTEGER,
                    age_max INTEGER,
                    requirements TEXT,
                    schedule TEXT,
                    rating REAL DEFAULT 0,
                    price_4 INTEGER,
                    price_8 INTEGER,
                    price_unlimited INTEGER,
                    photo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (center_id) REFERENCES centers(center_id)
                )
            """)

            # Универсальные абонементы (управляются админом)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscription_templates (
                    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    tariff TEXT NOT NULL,
                    lessons_total INTEGER,
                    price REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users(user_id)
                )
            """)
            
            # Абонементы пользователей (универсальные, без привязки к центру/курсу)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    child_id INTEGER,
                    template_id INTEGER,
                    tariff TEXT,
                    lessons_total INTEGER,
                    lessons_remaining INTEGER,
                    qr_code TEXT UNIQUE,
                    status TEXT DEFAULT 'active',
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (child_id) REFERENCES children(child_id),
                    FOREIGN KEY (template_id) REFERENCES subscription_templates(template_id)
                )
            """)

            # Занятия (загружаются партнерами)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    center_id INTEGER,
                    course_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    duration INTEGER,
                    teacher_id INTEGER,
                    max_students INTEGER,
                    current_students INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (center_id) REFERENCES centers(center_id),
                    FOREIGN KEY (course_id) REFERENCES courses(course_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                )
            """)
            
            # Посещения (универсальные, без привязки к курсу)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER,
                    user_id INTEGER,
                    child_id INTEGER,
                    center_id INTEGER,
                    lesson_id INTEGER,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (child_id) REFERENCES children(child_id),
                    FOREIGN KEY (center_id) REFERENCES centers(center_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id)
                )
            """)

            # Платежи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER,
                    user_id INTEGER,
                    amount REAL,
                    currency TEXT DEFAULT 'KZT',
                    method TEXT,
                    status TEXT DEFAULT 'pending',
                    transaction_id TEXT,
                    invoice_id TEXT,
                    airba_payment_id TEXT,
                    redirect_url TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Возвраты платежей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payment_refunds (
                    refund_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER,
                    airba_refund_id TEXT,
                    ext_id TEXT,
                    amount REAL,
                    reason TEXT,
                    status TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
                )
            """)

            # Отзывы
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER,
                    user_id INTEGER,
                    rating INTEGER,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            await db.commit()
            
            # Миграция: добавляем template_id в subscriptions, если его нет
            await self._migrate_subscriptions_table(db)

    async def _migrate_subscriptions_table(self, db):
        """Миграция таблицы subscriptions для добавления template_id"""
        try:
            # Проверяем, существует ли колонка template_id
            async with db.execute("PRAGMA table_info(subscriptions)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
            
            # Если template_id отсутствует, добавляем его
            if 'template_id' not in column_names:
                logger.info("Добавляем колонку template_id в таблицу subscriptions...")
                await db.execute("""
                    ALTER TABLE subscriptions 
                    ADD COLUMN template_id INTEGER
                """)
                await db.commit()
                logger.info("Колонка template_id успешно добавлена")
            
            # Если есть старые колонки course_id и center_id, их можно оставить для обратной совместимости
            # или удалить, если они больше не нужны
            
        except Exception as e:
            logger.error(f"Ошибка при миграции таблицы subscriptions: {e}", exc_info=True)
            # Не прерываем выполнение, если миграция не удалась

    # Методы для работы с пользователями
    async def get_user(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_user(self, user_id: int, username: str = None, full_name: str = None, role: str = ROLE_USER):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, full_name, role)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, full_name, role))
            await db.commit()

    async def update_user_role(self, user_id: int, role: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
            await db.commit()

    async def update_user_city(self, user_id: int, city: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET city = ? WHERE user_id = ?", (city, user_id))
            await db.commit()

    # Методы для работы с детьми
    async def add_child(self, parent_id: int, name: str, age: int):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO children (parent_id, name, age)
                VALUES (?, ?, ?)
            """, (parent_id, name, age))
            await db.commit()
            return cursor.lastrowid

    async def get_children(self, parent_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM children WHERE parent_id = ?", (parent_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_child(self, child_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM children WHERE child_id = ?", (child_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # Методы для работы с центрами
    async def create_center(self, partner_id: int, data: dict):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO centers (partner_id, name, city, address, phone, category, description, logo, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                partner_id,
                data.get("name"),
                data.get("city"),
                data.get("address"),
                data.get("phone"),
                data.get("category"),
                data.get("description"),
                data.get("logo"),
                data.get("status", STATUS_PENDING)
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_centers(self, city: str = None, category: str = None, status: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM centers WHERE 1=1"
            params = []
            
            if city:
                query += " AND city = ?"
                params.append(city)
            if category:
                query += " AND category = ?"
                params.append(category)
            if status:
                query += " AND status = ?"
                params.append(status)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_center(self, center_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM centers WHERE center_id = ?", (center_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_center_status(self, center_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE centers SET status = ? WHERE center_id = ?", (status, center_id))
            await db.commit()

    # Методы для работы с курсами
    async def create_course(self, center_id: int, data: dict):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO courses (center_id, name, description, category, age_min, age_max, requirements, 
                                   schedule, price_4, price_8, price_unlimited, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                center_id,
                data.get("name"),
                data.get("description"),
                data.get("category"),
                data.get("age_min"),
                data.get("age_max"),
                data.get("requirements"),
                data.get("schedule"),
                data.get("price_4"),
                data.get("price_8"),
                data.get("price_unlimited"),
                data.get("photo")
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_courses(self, city: str = None, category: str = None, age: int = None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = """
                SELECT c.*, ce.name as center_name, ce.address, ce.city, ce.phone
                FROM courses c
                JOIN centers ce ON c.center_id = ce.center_id
                WHERE ce.status = 'approved' AND 1=1
            """
            params = []
            
            if city:
                query += " AND ce.city = ?"
                params.append(city)
            if category:
                query += " AND c.category = ?"
                params.append(category)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                courses = [dict(row) for row in rows]
                # Фильтрация по возрасту на уровне Python
                if age:
                    courses = [c for c in courses if 
                              (not c.get("age_min") or c["age_min"] <= age) and
                              (not c.get("age_max") or c["age_max"] >= age)]
                return courses

    async def get_course(self, course_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT c.*, ce.name as center_name, ce.address, ce.city, ce.phone
                FROM courses c
                JOIN centers ce ON c.center_id = ce.center_id
                WHERE c.course_id = ?
            """, (course_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # Методы для работы с шаблонами абонементов (админ)
    async def create_subscription_template(self, name: str, description: str, tariff: str, 
                                          lessons_total: int, price: float, created_by: int):
        """Создать шаблон универсального абонемента"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO subscription_templates (name, description, tariff, lessons_total, price, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, tariff, lessons_total, price, created_by))
            await db.commit()
            return cursor.lastrowid

    async def get_subscription_templates(self, active_only: bool = True):
        """Получить все шаблоны абонементов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM subscription_templates"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY price ASC"
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_subscription_template(self, template_id: int):
        """Получить шаблон абонемента по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM subscription_templates WHERE template_id = ?", (template_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_subscription_template(self, template_id: int, name: str = None, 
                                          description: str = None, price: float = None, 
                                          is_active: bool = None):
        """Обновить шаблон абонемента"""
        async with aiosqlite.connect(self.db_path) as db:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if price is not None:
                updates.append("price = ?")
                params.append(price)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            if updates:
                params.append(template_id)
                await db.execute(
                    f"UPDATE subscription_templates SET {', '.join(updates)} WHERE template_id = ?",
                    params
                )
                await db.commit()
                return True
            return False

    async def delete_subscription_template(self, template_id: int):
        """Удалить шаблон абонемента"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE subscription_templates SET is_active = 0 WHERE template_id = ?", (template_id,))
            await db.commit()
            return True

    # Методы для работы с абонементами пользователей
    async def create_subscription(self, user_id: int, template_id: int, qr_code: str, child_id: int = None):
        """Создать универсальный абонемент из шаблона"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем данные шаблона
            template = await self.get_subscription_template(template_id)
            if not template:
                return None
            
            cursor = await db.execute("""
                INSERT INTO subscriptions (user_id, child_id, template_id, tariff, 
                                         lessons_total, lessons_remaining, qr_code, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                user_id,
                child_id,
                template_id,
                template["tariff"],
                template["lessons_total"],
                template["lessons_total"],
                qr_code
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_user_subscriptions(self, user_id: int, child_id: int = None):
        """Получить универсальные абонементы пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if child_id:
                query = """
                    SELECT s.*, st.name as template_name, st.description as template_description
                    FROM subscriptions s
                    LEFT JOIN subscription_templates st ON s.template_id = st.template_id
                    WHERE s.child_id = ? AND s.status = 'active'
                """
                params = (child_id,)
            else:
                query = """
                    SELECT s.*, st.name as template_name, st.description as template_description
                    FROM subscriptions s
                    LEFT JOIN subscription_templates st ON s.template_id = st.template_id
                    WHERE s.user_id = ? AND s.child_id IS NULL AND s.status = 'active'
                """
                params = (user_id,)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_subscription_by_qr(self, qr_code: str):
        """Получить универсальный абонемент по QR-коду"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT s.*, st.name as template_name, st.description as template_description,
                       u.user_id as owner_id, u.full_name as owner_name,
                       ch.name as child_name, ch.age as child_age
                FROM subscriptions s
                LEFT JOIN subscription_templates st ON s.template_id = st.template_id
                LEFT JOIN users u ON s.user_id = u.user_id
                LEFT JOIN children ch ON s.child_id = ch.child_id
                WHERE s.qr_code = ? AND s.status = 'active'
            """, (qr_code,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def record_visit(self, subscription_id: int, center_id: int, lesson_id: int = None):
        """Запись посещения с защитой от дублирования (универсальный абонемент работает во всех центрах)"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем данные абонемента
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM subscriptions WHERE subscription_id = ?", (subscription_id,)) as cursor:
                sub = await cursor.fetchone()
                if not sub:
                    return False
            
            sub = dict(sub)
            
            # Проверяем, что абонемент активен
            if sub.get("status") != "active":
                return False
            
            # Проверяем, что занятия не закончились (для не безлимитных)
            if sub["tariff"] != "unlimited" and sub.get("lessons_remaining", 0) <= 0:
                return False
            
            # Проверяем на дублирование (посещение в последние 5 минут в этом центре)
            from datetime import datetime, timedelta
            five_min_ago = datetime.now() - timedelta(minutes=5)
            five_min_ago_str = five_min_ago.strftime('%Y-%m-%d %H:%M:%S')
            
            async with db.execute("""
                SELECT COUNT(*) as count FROM visits
                WHERE subscription_id = ? 
                AND center_id = ?
                AND datetime(visited_at) > datetime(?)
            """, (subscription_id, center_id, five_min_ago_str)) as cursor:
                recent_visit = await cursor.fetchone()
                if recent_visit and recent_visit["count"] > 0:
                    return False  # Уже было посещение в последние 5 минут в этом центре
            
            # Записываем посещение (универсальный абонемент работает во всех центрах)
            await db.execute("""
                INSERT INTO visits (subscription_id, user_id, child_id, center_id, lesson_id, visited_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (subscription_id, sub.get("user_id"), sub.get("child_id"), center_id, lesson_id))
            
            # Уменьшаем количество оставшихся занятий (если не безлимит)
            if sub["tariff"] != "unlimited":
                # Сначала уменьшаем количество занятий
                await db.execute("""
                    UPDATE subscriptions 
                    SET lessons_remaining = lessons_remaining - 1
                    WHERE subscription_id = ? AND lessons_remaining > 0
                """, (subscription_id,))
                
                # Проверяем, закончились ли занятия после уменьшения
                async with db.execute("""
                    SELECT lessons_remaining FROM subscriptions WHERE subscription_id = ?
                """, (subscription_id,)) as cursor:
                    result = await cursor.fetchone()
                    if result and result["lessons_remaining"] <= 0:
                        # Если занятия закончились, деактивируем абонемент
                        await db.execute("""
                            UPDATE subscriptions 
                            SET status = 'expired'
                            WHERE subscription_id = ? AND lessons_remaining <= 0
                        """, (subscription_id,))
            
            await db.commit()
            return True

    async def get_visit_stats(self, user_id: int, child_id: int = None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if child_id:
                # Статистика для ребёнка
                async with db.execute("""
                    SELECT 
                        COUNT(v.visit_id) as visits_count,
                        SUM(CASE WHEN s.lessons_total > 0 THEN s.lessons_total ELSE 0 END) as total_lessons,
                        SUM(CASE WHEN s.lessons_remaining >= 0 THEN s.lessons_remaining ELSE 0 END) as remaining_lessons
                    FROM subscriptions s
                    LEFT JOIN visits v ON s.subscription_id = v.subscription_id
                    WHERE s.child_id = ?
                """, (child_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else {"visits_count": 0, "total_lessons": 0, "remaining_lessons": 0}
            else:
                # Статистика для взрослого
                async with db.execute("""
                    SELECT 
                        COUNT(v.visit_id) as visits_count,
                        SUM(CASE WHEN s.lessons_total > 0 THEN s.lessons_total ELSE 0 END) as total_lessons,
                        SUM(CASE WHEN s.lessons_remaining >= 0 THEN s.lessons_remaining ELSE 0 END) as remaining_lessons
                    FROM subscriptions s
                    LEFT JOIN visits v ON s.subscription_id = v.subscription_id
                    WHERE s.user_id = ? AND s.child_id IS NULL
                """, (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else {"visits_count": 0, "total_lessons": 0, "remaining_lessons": 0}

    # Методы для партнёров
    async def get_partner_center(self, partner_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM centers WHERE partner_id = ?", (partner_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_center_students(self, center_id: int):
        """Получить студентов, которые посещали этот центр (универсальные абонементы)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT DISTINCT 
                    s.user_id, s.child_id, u.full_name, ch.name as child_name,
                    s.lessons_remaining, s.subscription_id
                FROM subscriptions s
                LEFT JOIN users u ON s.user_id = u.user_id
                LEFT JOIN children ch ON s.child_id = ch.child_id
                WHERE s.status = 'active'
                AND EXISTS (
                    SELECT 1 FROM visits v 
                    WHERE v.subscription_id = s.subscription_id 
                    AND v.center_id = ?
                )
            """, (center_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_center_analytics(self, center_id: int, month: int = None, year: int = None):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Посещения
            visits_query = """
                SELECT COUNT(*) as visits_count
                FROM visits
                WHERE center_id = ?
            """
            visits_params = (center_id,)
            
            if month and year:
                visits_query += " AND strftime('%m', visited_at) = ? AND strftime('%Y', visited_at) = ?"
                visits_params = (center_id, f"{month:02d}", str(year))
            
            async with db.execute(visits_query, visits_params) as cursor:
                visits_row = await cursor.fetchone()
                visits_count = visits_row["visits_count"] if visits_row else 0
            
            # Посещения в этом центре (универсальные абонементы)
            # Продажи абонементов теперь не привязаны к центру, поэтому считаем только посещения
            sales_count = 0
            total_revenue = 0
            
            return {
                "visits_count": visits_count,
                "sales_count": sales_count,
                "total_revenue": total_revenue or 0
            }

    # Методы для админа
    async def get_pending_centers(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM centers WHERE status = 'pending'") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Методы для работы с платежами
    async def create_payment(self, user_id: int, subscription_id: int, amount: float, 
                           currency: str = "KZT", invoice_id: str = None, 
                           airba_payment_id: str = None, redirect_url: str = None, 
                           status: str = "pending"):
        """Создать платеж"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO payments (user_id, subscription_id, amount, currency, 
                                    invoice_id, airba_payment_id, redirect_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, subscription_id, amount, currency, invoice_id, 
                  airba_payment_id, redirect_url, status))
            await db.commit()
            return cursor.lastrowid

    async def get_payment(self, payment_id: int, user_id: int = None):
        """Получить платеж"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if user_id:
                async with db.execute(
                    "SELECT * FROM payments WHERE payment_id = ? AND user_id = ?",
                    (payment_id, user_id)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
            else:
                async with db.execute(
                    "SELECT * FROM payments WHERE payment_id = ?",
                    (payment_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None

    async def update_payment_status(self, payment_id: int, status: str, 
                                  transaction_id: str = None, error_message: str = None):
        """Обновить статус платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            if status == "success":
                await db.execute("""
                    UPDATE payments 
                    SET status = ?, transaction_id = ?, processed_at = CURRENT_TIMESTAMP,
                        error_message = ?
                    WHERE payment_id = ?
                """, (status, transaction_id, error_message, payment_id))
            else:
                await db.execute("""
                    UPDATE payments 
                    SET status = ?, transaction_id = ?, error_message = ?
                    WHERE payment_id = ?
                """, (status, transaction_id, error_message, payment_id))
            await db.commit()

    async def get_user_payments(self, user_id: int):
        """Получить все платежи пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def create_payment_refund(self, payment_id: int, airba_refund_id: str, 
                                   ext_id: str, amount: float, reason: str, status: str):
        """Создать возврат платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO payment_refunds (payment_id, airba_refund_id, ext_id, amount, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (payment_id, airba_refund_id, ext_id, amount, reason, status))
            await db.commit()
            return cursor.lastrowid

    # Методы для работы с преподавателями
    async def create_teacher(self, center_id: int, name: str, description: str = None):
        """Создать преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO teachers (center_id, name, description)
                VALUES (?, ?, ?)
            """, (center_id, name, description))
            await db.commit()
            return cursor.lastrowid

    async def get_teachers(self, center_id: int):
        """Получить всех преподавателей центра"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM teachers WHERE center_id = ?", (center_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_teacher(self, teacher_id: int):
        """Получить преподавателя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_teacher(self, teacher_id: int, name: str = None, description: str = None):
        """Обновить данные преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if updates:
                params.append(teacher_id)
                await db.execute(
                    f"UPDATE teachers SET {', '.join(updates)} WHERE teacher_id = ?",
                    params
                )
                await db.commit()
                return True
            return False

    async def delete_teacher(self, teacher_id: int):
        """Удалить преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            await db.commit()
            return True

    # Методы для работы с отзывами
    async def create_review(self, course_id: int, user_id: int, rating: int, comment: str = None):
        """Создать отзыв"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, не оставлял ли пользователь уже отзыв на этот курс
            async with db.execute("""
                SELECT review_id FROM reviews 
                WHERE course_id = ? AND user_id = ?
            """, (course_id, user_id)) as cursor:
                existing = await cursor.fetchone()
                if existing:
                    return None  # Отзыв уже существует
            
            cursor = await db.execute("""
                INSERT INTO reviews (course_id, user_id, rating, comment)
                VALUES (?, ?, ?, ?)
            """, (course_id, user_id, rating, comment))
            await db.commit()
            
            # Обновляем рейтинг курса
            await self._update_course_rating(course_id)
            
            return cursor.lastrowid

    async def get_reviews(self, course_id: int, limit: int = 20):
        """Получить отзывы о курсе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT r.*, u.full_name, u.username
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.user_id
                WHERE r.course_id = ?
                ORDER BY r.created_at DESC
                LIMIT ?
            """, (course_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_user_review(self, course_id: int, user_id: int):
        """Получить отзыв пользователя о курсе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reviews 
                WHERE course_id = ? AND user_id = ?
            """, (course_id, user_id)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def _update_course_rating(self, course_id: int):
        """Обновить средний рейтинг курса"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as count
                FROM reviews WHERE course_id = ?
            """, (course_id,)) as cursor:
                result = await cursor.fetchone()
                if result and result["count"] > 0:
                    avg_rating = result["avg_rating"]
                    await db.execute("""
                        UPDATE courses SET rating = ? WHERE course_id = ?
                    """, (round(avg_rating, 1), course_id))
                    await db.commit()

    # Методы для работы с преподавателями
    async def create_teacher(self, center_id: int, name: str, description: str = None):
        """Создать преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO teachers (center_id, name, description)
                VALUES (?, ?, ?)
            """, (center_id, name, description))
            await db.commit()
            return cursor.lastrowid

    async def get_teachers(self, center_id: int):
        """Получить всех преподавателей центра"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM teachers WHERE center_id = ?", (center_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_teacher(self, teacher_id: int):
        """Получить преподавателя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_teacher(self, teacher_id: int, name: str = None, description: str = None):
        """Обновить данные преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if updates:
                params.append(teacher_id)
                await db.execute(
                    f"UPDATE teachers SET {', '.join(updates)} WHERE teacher_id = ?",
                    params
                )
                await db.commit()
                return True
            return False

    async def delete_teacher(self, teacher_id: int):
        """Удалить преподавателя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            await db.commit()
            return True

    # Методы для работы с отзывами
    async def create_review(self, course_id: int, user_id: int, rating: int, comment: str = None):
        """Создать отзыв"""
        async with aiosqlite.connect(self.db_path) as db:
            # Проверяем, не оставлял ли пользователь уже отзыв на этот курс
            async with db.execute("""
                SELECT review_id FROM reviews 
                WHERE course_id = ? AND user_id = ?
            """, (course_id, user_id)) as cursor:
                existing = await cursor.fetchone()
                if existing:
                    return None  # Отзыв уже существует
            
            cursor = await db.execute("""
                INSERT INTO reviews (course_id, user_id, rating, comment)
                VALUES (?, ?, ?, ?)
            """, (course_id, user_id, rating, comment))
            await db.commit()
            
            # Обновляем рейтинг курса
            await self._update_course_rating(course_id)
            
            return cursor.lastrowid

    async def get_reviews(self, course_id: int, limit: int = 20):
        """Получить отзывы о курсе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT r.*, u.full_name, u.username
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.user_id
                WHERE r.course_id = ?
                ORDER BY r.created_at DESC
                LIMIT ?
            """, (course_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_user_review(self, course_id: int, user_id: int):
        """Получить отзыв пользователя о курсе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reviews 
                WHERE course_id = ? AND user_id = ?
            """, (course_id, user_id)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def _update_course_rating(self, course_id: int):
        """Обновить средний рейтинг курса"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT AVG(rating) as avg_rating, COUNT(*) as count
                FROM reviews WHERE course_id = ?
            """, (course_id,)) as cursor:
                result = await cursor.fetchone()
                if result and result["count"] > 0:
                    avg_rating = result["avg_rating"]
                    await db.execute("""
                        UPDATE courses SET rating = ? WHERE course_id = ?
                    """, (round(avg_rating, 1), course_id))
                    await db.commit()

