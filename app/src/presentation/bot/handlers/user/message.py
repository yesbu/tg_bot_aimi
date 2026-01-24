from aiogram import Router, F
from aiogram.types import Message
from dishka import FromDishka

from src.application.use_cases.subscription import GetActiveSubscriptionPlansUseCase
from src.presentation.bot.keyboards.inline_keyboards import (
    get_search_params_keyboard,
    get_subscription_plans_keyboard,
)


router = Router()


@router.message(F.text == "📚 Каталог курсов")
async def catalog_menu(message: Message):
    await message.answer(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message):
    await message.answer(
        "🆘 Поддержка\n\n"
        "Если у тебя есть вопросы, напиши нам:\n"
        "📧 support@example.com\n"
        "📱 +7 (XXX) XXX-XX-XX"
    )

# добавить проверку на наличие тарифов у пользователя
@router.message(F.text == "🎫 Мои абонементы")
async def my_subscriptions(
    message: Message,
    get_active_plans: FromDishka[GetActiveSubscriptionPlansUseCase]
):
    plans = await get_active_plans.execute()
    
    if not plans:
        await message.answer(
            "🎫 Доступные тарифы отсутствуют.\n\n"
            "Попробуйте позже."
        )
        return
    
    text = "💎 Наши тарифы:\n\n"
    for plan in plans:
        text += f"📅 {plan.name}\n"
        text += f"💰 {plan.price:,.0f} ₸\n"
        text += f"⏰ {plan.duration_months} мес\n"
        text += f"🎯 {plan.visits_limit} посещений\n"
        text += f"{plan.description}\n"
        text += "\n"
    
    await message.answer(
        text, 
        reply_markup=get_subscription_plans_keyboard(plans)
    )


@router.message(F.text == "🕒 Расписание")
async def schedule(message: Message):
    await message.answer(
        "🕒 Расписание\n\n"
        "Функция в разработке."
    )


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message):
    await message.answer(
        "📊 Статистика\n\n"
        "Функция в разработке."
    )


@router.message(F.text == "💳 Мои платежи")
async def my_payments(message: Message):
    await message.answer(
        "💳 История платежей\n\n"
        "Функция в разработке."
    )
