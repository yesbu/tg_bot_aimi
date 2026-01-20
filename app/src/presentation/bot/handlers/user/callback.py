from aiogram import Router, F
from aiogram.types import CallbackQuery
from dishka import FromDishka

from src.application.use_cases.city import GetAllCitiesUseCase
from src.application.use_cases.category import GetAllCategoriesUseCase
from src.application.use_cases.subscription import GetSubscriptionPlanByIdUseCase
from src.presentation.bot.keyboards.inline_keyboards import (
    get_cities_keyboard,
    get_categories_keyboard
)


router = Router()


@router.callback_query(F.data == "search_city")
async def select_city(
    callback: CallbackQuery,
    get_all_cities_use_case: FromDishka[GetAllCitiesUseCase]
):
    cities = await get_all_cities_use_case.execute()

    await callback.message.edit_text(
        "🏙 Выбери город:",
        reply_markup=get_cities_keyboard(cities)
    )
    await callback.answer()


@router.callback_query(F.data == "search_category")
async def select_category(
    callback: CallbackQuery,
    get_all_categories_use_case: FromDishka[GetAllCategoriesUseCase]
):
    categories = await get_all_categories_use_case.execute()

    await callback.message.edit_text(
        "📂 Выбери категорию:",
        reply_markup=get_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_plan_"))
async def buy_subscription_plan(
    callback: CallbackQuery,
    get_plan_by_id: FromDishka[GetSubscriptionPlanByIdUseCase]
):
    plan_id = int(callback.data.replace("buy_plan_", ""))

    plan = await get_plan_by_id.execute(plan_id)

    if not plan:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    text = (
        f"✅ Вы выбрали тариф:\n\n"
        f"📅 {plan.name}\n"
        f"💰 {plan.price:,.0f} ₸\n"
        f"⏰ {plan.duration_months} мес\n"
        f"🎯 {plan.visits_limit} посещений\n"
        f"{plan.description}"
    )

    await callback.message.edit_text(text)
    await callback.answer()
