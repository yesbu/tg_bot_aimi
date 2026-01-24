from aiogram import Router, F
from aiogram.types import Message
from dishka import FromDishka

from src.application.use_cases.subscription import (
    GetActiveSubscriptionPlansUseCase,
    GetUserActiveSubscriptionUseCase,
)
from src.application.use_cases.user import GetUserUseCase
from src.application.use_cases.payment import GetUserPaymentsUseCase
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

@router.message(F.text == "🎫 Мои абонементы")
async def my_subscriptions(
    message: Message,
    get_active_plans: FromDishka[GetActiveSubscriptionPlansUseCase],
    get_user: FromDishka[GetUserUseCase],
    get_user_subscription: FromDishka[GetUserActiveSubscriptionUseCase],
):
    user = await get_user.execute(message.from_user.id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return
    
    active_subscription = await get_user_subscription.execute(user.id)
    
    if active_subscription:
        days_left = active_subscription.days_remaining
        expires_date = active_subscription.expires_at.strftime("%d.%m.%Y")
        
        await message.answer(
            f"✅ У вас активная подписка!\n\n"
            f"📅 Действует до: {expires_date}\n"
            f"⏰ Осталось дней: {days_left}\n\n"
        )
        return
    
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


@router.message(F.text == "💳 Мои платежи")
async def my_payments(
    message: Message,
    get_user_payments: FromDishka[GetUserPaymentsUseCase],
):
    payments = await get_user_payments.execute(message.from_user.id, limit=10)
    
    if not payments:
        await message.answer(
            "💳 История платежей\n\n"
            "У вас пока нет платежей."
        )
        return
    
    text = "💳 История ваших платежей:\n\n"
    
    for payment in payments:
        status_emoji = {
            "NEW": "🆕",
            "new": "🆕",
            "PENDING": "⏳",
            "PROCESSING": "⏳",
            "auth": "⏳",
            "secure3D": "⏳",
            "SUCCEEDED": "✅",
            "success": "✅",
            "FAILED": "❌",
            "error": "❌",
            "CANCELLED": "🚫",
            "REFUNDED": "↩️",
            "refund": "↩️",
            "return": "↩️",
        }.get(payment.status.value, "❓")
        
        date = payment.created_at.strftime("%d.%m.%Y %H:%M") if payment.created_at else "—"
        
        text += f"{status_emoji} {payment.amount:,.0f} {payment.currency}\n"
        text += f"📅 {date}\n"
        text += f"📋 Статус: {payment.status.description}\n"
        
        if payment.payment_id:
            text += f"🔢 ID: {payment.payment_id[:20]}...\n"
        
        text += "\n"
    
    await message.answer(text)



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


