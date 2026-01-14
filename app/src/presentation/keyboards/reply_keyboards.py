from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог курсов")],
            [KeyboardButton(text="🎫 Мои абонементы")],
            [KeyboardButton(text="💳 Мои платежи")],
            [KeyboardButton(text="🕒 Расписание")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🆘 Поддержка")]
        ],
        resize_keyboard=True
    )


def get_parent_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧒 Мои дети")],
            [KeyboardButton(text="🎫 Купить абонемент")],
            [KeyboardButton(text="📅 Расписание")],
            [KeyboardButton(text="📊 Посещаемость")],
            [KeyboardButton(text="💳 Покупки")]
        ],
        resize_keyboard=True
    )


def get_child_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Показать QR")],
            [KeyboardButton(text="🕒 Расписание")],
            [KeyboardButton(text="📊 Моя статистика")]
        ],
        resize_keyboard=True
    )


def get_partner_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить центр")],
            [KeyboardButton(text="📋 Ученики")],
            [KeyboardButton(text="🧾 Сканировать QR")],
            [KeyboardButton(text="🗓 Расписание")],
            [KeyboardButton(text="🎓 Курсы")],
            [KeyboardButton(text="👩‍🏫 Преподаватели")],
            [KeyboardButton(text="📊 Аналитика")],
            [KeyboardButton(text="⚙ Настройки")]
        ],
        resize_keyboard=True
    )


def get_admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏢 Центры")],
            [KeyboardButton(text="👥 Пользователи")],
            [KeyboardButton(text="👶 Дети / Родители")],
            [KeyboardButton(text="🎫 Управление абонементами")],
            [KeyboardButton(text="🎫 Абонементы")],
            [KeyboardButton(text="💳 Оплаты")],
            [KeyboardButton(text="📝 Логи посещений")],
            [KeyboardButton(text="✅ Модерация")],
            [KeyboardButton(text="📢 Рассылки")]
        ],
        resize_keyboard=True
    )
