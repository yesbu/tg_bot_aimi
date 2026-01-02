from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🏫 Центры", callback_data="centers"),
            InlineKeyboardButton(text="📚 Курсы", callback_data="courses")
        ],
        [
            InlineKeyboardButton(text="🎫 Мои абонементы", callback_data="my_subscriptions"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")
        ],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_parent_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="👶 Мои дети", callback_data="my_children"),
            InlineKeyboardButton(text="➕ Добавить ребёнка", callback_data="add_child")
        ],
        [
            InlineKeyboardButton(text="🏫 Центры", callback_data="centers"),
            InlineKeyboardButton(text="📚 Курсы", callback_data="courses")
        ],
        [
            InlineKeyboardButton(text="🎫 Абонементы", callback_data="subscriptions"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")
        ],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_partner_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🏢 Мой центр", callback_data="my_center"),
            InlineKeyboardButton(text="📝 Заявки", callback_data="applications")
        ],
        [
            InlineKeyboardButton(text="📚 Курсы", callback_data="courses"),
            InlineKeyboardButton(text="👥 Преподаватели", callback_data="teachers")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Одобрить центры", callback_data="admin_approve_centers"),
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="🏫 Все центры", callback_data="admin_all_centers"),
            InlineKeyboardButton(text="📚 Все курсы", callback_data="admin_all_courses")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_statistics"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
