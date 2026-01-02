from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger
from dishka.integrations.aiogram import FromDishka

from src.application.services import UserService
from src.domain.enums import Role
from src.presentation.keyboards.main import get_main_menu, get_parent_menu


router = Router()


@router.message(Command("start"))
async def cmd_start(
    message: Message,
    state: FSMContext,
    user_service: FromDishka[UserService],
):
    try:
        await state.clear()
        
        logger.info(f"Processing /start from user {message.from_user.id}")
        
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name or "Пользователь"
        last_name = message.from_user.last_name
        
        if not first_name or len(first_name.strip()) < 2:
            first_name = "Пользователь"
        
        user = await user_service.get_or_create_user(
            telegram_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        
        logger.info(f"User {user_id} role: {user.role}")
        
        if user.role == Role.PARENT:
            await message.answer(
                f"👋 Добро пожаловать, {user.full_name}!\n\n"
                "Выберите действие:",
                reply_markup=get_parent_menu()
            )
        elif user.role == Role.PARTNER:
            await message.answer(
                f"👋 Добро пожаловать, {user.full_name}!\n\n"
                "Управляйте своим центром:",
                reply_markup=get_main_menu()
            )
        elif user.role == Role.ADMIN:
            await message.answer(
                f"👋 Добро пожаловать, {user.full_name}!\n\n"
                "Панель администратора:",
                reply_markup=get_main_menu()
            )
        else:
            welcome_text = f"👋 Привет, {user.full_name}!\n\n"
            welcome_text += "Здесь ты можешь находить образовательные центры, покупать абонементы "
            welcome_text += "и посещать занятия по QR-коду.\n\n"
            welcome_text += "Выберите действие:"
            
            await message.answer(
                welcome_text,
                reply_markup=get_main_menu()
            )
        
        logger.info(f"Successfully processed /start for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing /start: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке команды.\n\n"
            "Попробуйте ещё раз или обратитесь в поддержку."
        )

