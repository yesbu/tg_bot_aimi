from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import ICenterService
from src.presentation.bot.states.admin_states import AdminModerationStates


router = Router()


@router.callback_query(F.data.startswith("approve_center_"))
async def approve_center(
    callback: CallbackQuery,
    center_service: FromDishka[ICenterService]
):
    center_id = int(callback.data.replace("approve_center_", ""))
    
    try:
        await center_service.approve_center(center_id)
        
        await callback.message.edit_text(
            f"✅ Центр одобрен!\n\n"
            f"Партнер получит уведомление."
        )
        await callback.answer("Центр одобрен!")
    except Exception as e:
        logger.error(f"Error approving center: {e}", exc_info=True)
        await callback.answer("Ошибка при одобрении центра", show_alert=True)


@router.callback_query(F.data.startswith("reject_center_"))
async def reject_center_start(
    callback: CallbackQuery,
    state: FSMContext
):
    center_id = int(callback.data.replace("reject_center_", ""))
    
    await state.update_data(rejecting_center_id=center_id)
    
    await callback.message.edit_text(
        "❌ Отклонение заявки\n\n"
        "Введи причину отклонения:"
    )
    await state.set_state(AdminModerationStates.rejection_reason)
    await callback.answer()


@router.message(AdminModerationStates.rejection_reason)
async def rejection_reason_received(
    message: Message,
    state: FSMContext,
    center_service: FromDishka[ICenterService]
):
    reason = message.text.strip()
    data = await state.get_data()
    center_id = data.get("rejecting_center_id")
    
    try:
        await center_service.reject_center(center_id, reason)
        
        await message.answer(
            f"❌ Центр отклонен!\n\n"
            f"Причина: {reason}\n\n"
            f"Партнер получит уведомление."
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error rejecting center: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при отклонении центра."
        )
        await state.clear()
