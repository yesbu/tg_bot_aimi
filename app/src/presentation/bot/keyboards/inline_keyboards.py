from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from src.domain.entities import SubscriptionPlan, City, Category


def get_search_params_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏙 Город", callback_data="search_city")],
            [InlineKeyboardButton(text="📂 Категория", callback_data="search_category")],
            [InlineKeyboardButton(text="🎂 Возраст", callback_data="search_age")],
            [InlineKeyboardButton(text="⭐ Рейтинг", callback_data="search_rating")]
        ]
    )


def get_cities_keyboard(cities: list[City]) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(cities), 2):
        city = cities[i]
        row = [InlineKeyboardButton(text=city.name, callback_data=f"city_{city.id}")]
        
        if i + 1 < len(cities):
            city_2 = cities[i + 1]
            row.append(InlineKeyboardButton(text=city_2.name, callback_data=f"city_{city_2.id}"))
        
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(categories), 2):
        cat = categories[i]
        row = [InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")]
        
        if i + 1 < len(categories):
            cat_2 = categories[i + 1]
            row.append(InlineKeyboardButton(text=cat_2.name, callback_data=f"category_{cat_2.id}"))
        
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_parent_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👶 Добавить ребёнка", callback_data="parent_add_child")],
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="parent_skip")]
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


def get_payment_flow_keyboard(payment_url: str, payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", web_app=WebAppInfo(url=payment_url))],
            [InlineKeyboardButton(text="✅ Проверить платеж", callback_data=f"check_payment_{payment_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_payment_{payment_id}")]
        ]
    )
