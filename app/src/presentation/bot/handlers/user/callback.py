from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from src.application.use_cases.subscription import BuySubscriptionPlanUseCase
from src.application.use_cases.city import GetAllCitiesUseCase
from src.application.use_cases.category import GetAllCategoriesUseCase
from src.application.use_cases.payment import CheckPaymentStatusUseCase
from src.infrastructure.payment.status import PaymentStatusEnum
from src.presentation.bot.keyboards.inline_keyboards import (
    get_cities_keyboard,
    get_categories_keyboard,
    get_payment_flow_keyboard
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
    buy_subscription_use_case: FromDishka[BuySubscriptionPlanUseCase]
):
    plan_id = int(callback.data.replace("buy_plan_", ""))
    user_id = callback.from_user.id
    
    result = await buy_subscription_use_case.execute(user_id, plan_id)
    
    if not result.success:
        await callback.answer(result.error_message, show_alert=True)
        return
    
    if result.redirect_url:
        await callback.message.answer(
            f"💳 Оплата абонемента\n\n"
            f"Абонемент: {result.plan.name}\n"
            f"Сумма: {result.plan.price:,.0f} ₸\n\n"
            f"Перейдите по ссылке для оплаты:",
            reply_markup=get_payment_flow_keyboard(
                payment_url=result.redirect_url,
                payment_id=result.payment_id or "0",
                subscription_id=0
            )
        )
    else:
        await callback.message.answer(
            "⚠️ Ошибка при создании ссылки на оплату. Обратитесь в поддержку."
        )
    
    await callback.answer()
    

@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment_status(
    callback: CallbackQuery,
    state: FSMContext,
    check_payment_use_case: FromDishka[CheckPaymentStatusUseCase],
):
    payment_id = callback.data.replace("check_payment_", "")
    
    result = await check_payment_use_case.execute(payment_id)
    
    if not result.success:
        await callback.message.answer(
            f"❌ {result.error_message}"
        )
        await callback.answer()
        return
    
    if result.status == PaymentStatusEnum.SUCCESS:
        await callback.message.answer(
            "✅ Платеж прошел успешно!\n\n"
            "🎉 Абонемент активирован!"
        )
        await state.clear()
        
    elif result.status == PaymentStatusEnum.ERROR:
        error_msg = result.error_code.description if result.error_code else "Неизвестная ошибка"
        await callback.message.answer(
            f"❌ Платеж не прошел\n\n"
            f"Ошибка: {error_msg}\n\n"
            "Попробуйте оплатить снова или обратитесь в поддержку."
        )
        
    elif result.status in [PaymentStatusEnum.NEW, PaymentStatusEnum.SECURE_3D, PaymentStatusEnum.AUTH]:
        await callback.message.answer(
            f"⏳ Статус платежа: {result.status.description}\n\n"
            "Ожидаем подтверждения платежа..."
        )
        
    elif result.status in [PaymentStatusEnum.RETURN, PaymentStatusEnum.REFUND]:
        await callback.message.answer(
            f"↩️ Платеж возвращен\n\n"
            f"Статус: {result.status.description}"
        )
        
    else:
        await callback.message.answer(
            f"📋 Статус платежа: {result.status.description}\n\n"
            "Обратитесь в поддержку для уточнения."
        )
    
    await callback.answer()


    