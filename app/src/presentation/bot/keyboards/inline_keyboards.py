from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.domain.entities import SubscriptionPlan


def get_search_params_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏙 Город", callback_data="search_city")],
            [InlineKeyboardButton(text="📂 Категория", callback_data="search_category")],
            [InlineKeyboardButton(text="🎂 Возраст", callback_data="search_age")],
            [InlineKeyboardButton(text="⭐ Рейтинг", callback_data="search_rating")]
        ]
    )


def get_cities_keyboard(cities: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(cities), 2):
        city_id, city_name = cities[i]
        row = [InlineKeyboardButton(text=city_name, callback_data=f"city_{city_id}")]
        
        if i + 1 < len(cities):
            city_id_2, city_name_2 = cities[i + 1]
            row.append(InlineKeyboardButton(text=city_name_2, callback_data=f"city_{city_id_2}"))
        
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_categories_keyboard(categories: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(categories), 2):
        cat_id, cat_name = categories[i]
        row = [InlineKeyboardButton(text=cat_name, callback_data=f"category_{cat_id}")]
        
        if i + 1 < len(categories):
            cat_id_2, cat_name_2 = categories[i + 1]
            row.append(InlineKeyboardButton(text=cat_name_2, callback_data=f"category_{cat_id_2}"))
        
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_course_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Подробнее", callback_data=f"course_detail_{course_id}")],
            [InlineKeyboardButton(text="🛒 Купить абонемент", callback_data=f"buy_course_{course_id}")]
        ]
    )


def get_course_detail_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить абонемент", callback_data=f"buy_course_{course_id}")],
            [InlineKeyboardButton(text="💬 Посмотреть отзывы", callback_data=f"reviews_{course_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_catalog")]
        ]
    )


def get_tariff_keyboard(
    course_id: int,
    price_4: int | None = None,
    price_8: int | None = None,
    price_unlimited: int | None = None
) -> InlineKeyboardMarkup:
    keyboard = []
    
    if price_4:
        keyboard.append([InlineKeyboardButton(
            text=f"4 занятия — {price_4:,}₸",
            callback_data=f"tariff_{course_id}_4"
        )])
    
    if price_8:
        keyboard.append([InlineKeyboardButton(
            text=f"8 занятий — {price_8:,}₸",
            callback_data=f"tariff_{course_id}_8"
        )])
    
    if price_unlimited:
        keyboard.append([InlineKeyboardButton(
            text=f"Безлимит — {price_unlimited:,}₸",
            callback_data=f"tariff_{course_id}_unlimited"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"course_detail_{course_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Kaspi", callback_data=f"payment_kaspi_{subscription_id}")],
            [InlineKeyboardButton(text="💳 Telegram Payments", callback_data=f"payment_telegram_{subscription_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
        ]
    )


def get_subscription_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📷 Показать QR", callback_data=f"show_qr_{subscription_id}")],
            [InlineKeyboardButton(text="🔄 Продлить", callback_data=f"extend_{subscription_id}")],
            [InlineKeyboardButton(text="📜 История", callback_data=f"history_{subscription_id}")]
        ]
    )


def get_children_keyboard(children) -> InlineKeyboardMarkup:
    keyboard = []
    for child in children:
        keyboard.append([InlineKeyboardButton(
            text=f"{child.name} ({child.age} лет)",
            callback_data=f"select_child_{child.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_parent_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_moderation_keyboard(center_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_center_{center_id}")],
            [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_center_{center_id}")]
        ]
    )


def get_parent_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👶 Добавить ребёнка", callback_data="parent_add_child")],
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="parent_skip")]
        ]
    )


def get_review_keyboard(course_id: int, can_add_review: bool = True) -> InlineKeyboardMarkup:
    keyboard = []
    
    if can_add_review:
        keyboard.append([InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=f"add_review_{course_id}")])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"course_detail_{course_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_rating_keyboard(course_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ 1", callback_data=f"rating_{course_id}_1"),
                InlineKeyboardButton(text="⭐⭐ 2", callback_data=f"rating_{course_id}_2"),
                InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data=f"rating_{course_id}_3")
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data=f"rating_{course_id}_4"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data=f"rating_{course_id}_5")
            ],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data=f"course_detail_{course_id}")]
        ]
    )


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
        ]
    )


def get_subscription_plans_keyboard(plans: list[SubscriptionPlan]) -> InlineKeyboardMarkup:
    keyboard = []
    
    for plan in plans:
        button_text = f"📅 {plan.duration_months} {'месяц' if plan.duration_months == 1 else 'месяца' if plan.duration_months < 5 else 'месяцев'} - {plan.price:,.0f} ₸"
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"buy_plan_{plan.id}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
