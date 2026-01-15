from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import ICenterService, IUserService
from src.presentation.bot.keyboards.inline_keyboards import get_moderation_keyboard
from src.presentation.bot.states.admin_states import BroadcastStates


router = Router()


@router.message(F.text == "🔍 Модерация центров")
async def moderation_menu(
    message: Message,
    center_service: FromDishka[ICenterService]
):
    pending_centers = await center_service.get_pending_centers()
    
    if not pending_centers:
        await message.answer(
            "✅ Нет центров на модерации!\n\n"
            "Все заявки обработаны."
        )
        return
    
    for center in pending_centers:
        text = f"🏢 **{center.name}**\n\n"
        text += f"📍 Город: {center.city}\n"
        text += f"📫 Адрес: {center.address or 'Не указан'}\n"
        text += f"📞 Телефон: {center.phone or 'Не указан'}\n"
        
        if center.description:
            text += f"\n📝 Описание:\n{center.description}\n"
        
        text += f"\nПартнер ID: {center.partner_id}"
        
        await message.answer(
            text,
            reply_markup=get_moderation_keyboard(center.id)
        )


@router.message(F.text == "📋 Шаблоны абонементов")
async def templates_menu(message: Message):
    await message.answer(
        "📋 Управление шаблонами абонементов\n\n"
        "Функции:\n"
        "• Создать шаблон\n"
        "• Просмотр списка\n"
        "• Редактирование\n"
        "• Удаление\n\n"
        "Функционал в разработке..."
    )


@router.message(F.text == "📢 Рассылка")
async def broadcast_start(message: Message, state: FSMContext):
    await message.answer(
        "📢 Создание рассылки\n\n"
        "Введи текст сообщения для рассылки всем пользователям:"
    )
    await state.set_state(BroadcastStates.waiting_for_broadcast_message)


@router.message(BroadcastStates.waiting_for_broadcast_message)
async def broadcast_message_received(message: Message, state: FSMContext):
    broadcast_text = message.text
    
    await state.update_data(broadcast_message=broadcast_text)
    
    await message.answer(
        f"📢 Предпросмотр рассылки:\n\n"
        f"{broadcast_text}\n\n"
        f"Отправить всем пользователям?\n"
        f"Напиши 'ДА' для подтверждения или 'НЕТ' для отмены."
    )
    await state.set_state(BroadcastStates.confirming_broadcast)


@router.message(BroadcastStates.confirming_broadcast)
async def broadcast_confirmed(
    message: Message,
    state: FSMContext,
    user_service: FromDishka[IUserService]
):
    if message.text.upper() != "ДА":
        await message.answer("❌ Рассылка отменена.")
        await state.clear()
        return
    
    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")
    
    try:
        users = await user_service.get_all_users()
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await message.bot.send_message(
                    chat_id=user.telegram_id,
                    text=broadcast_message
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to {user.telegram_id}: {e}")
                failed_count += 1
        
        await message.answer(
            f"✅ Рассылка завершена!\n\n"
            f"Отправлено: {sent_count}\n"
            f"Ошибок: {failed_count}"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Broadcast error: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при выполнении рассылки."
        )
        await state.clear()


@router.message(F.text == "👥 Пользователи")
async def users_menu(
    message: Message,
    user_service: FromDishka[IUserService]
):
    try:
        users = await user_service.get_all_users()
        
        total_users = len(users)
        users_by_role = {}
        
        for user in users:
            role = user.role.value if hasattr(user, 'role') else 'unknown'
            users_by_role[role] = users_by_role.get(role, 0) + 1
        
        text = "👥 Статистика пользователей\n\n"
        text += f"Всего: {total_users}\n\n"
        
        for role, count in users_by_role.items():
            text += f"• {role}: {count}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error getting users: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при получении списка пользователей."
        )


@router.message(F.text == "📊 Статистика системы")
async def system_stats(
    message: Message,
    center_service: FromDishka[ICenterService],
    user_service: FromDishka[IUserService]
):
    try:
        users = await user_service.get_all_users()
        centers = await center_service.get_all_centers()
        
        approved_centers = [c for c in centers if c.status.value == "approved"]
        pending_centers = [c for c in centers if c.status.value == "pending"]
        
        text = "📊 Статистика системы\n\n"
        text += f"👥 Пользователей: {len(users)}\n"
        text += f"🏢 Центров: {len(centers)}\n"
        text += f"  ✅ Одобрено: {len(approved_centers)}\n"
        text += f"  ⏳ На модерации: {len(pending_centers)}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error getting system stats: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при получении статистики."
        )
