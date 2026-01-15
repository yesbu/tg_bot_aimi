from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import IUserService
from src.presentation.bot.keyboards.reply_keyboards import get_parent_menu
from src.presentation.bot.keyboards.inline_keyboards import get_parent_start_keyboard


router = Router()


@router.message(Command("start"))
async def cmd_start(
    message: Message,
    state: FSMContext,
    user_service: FromDishka[IUserService]
):
    await state.clear()
    
    logger.info(f"Processing /start from parent {message.from_user.id}")
    
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or "Пользователь"
    last_name = message.from_user.last_name
    
    user = await user_service.get_or_create_user(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    
    full_name = user.full_name
    
    await message.answer(
        f"👋 Привет, {full_name}!\n\n"
        "Ты родитель? Хотите добавить ребёнка?",
        reply_markup=get_parent_start_keyboard()
    )
    
    logger.info(f"Successfully processed /start for parent {telegram_id}")


@router.message(Command("cancel"))
async def cmd_cancel(
    message: Message,
    state: FSMContext
):
    current_state = await state.get_state()
    
    if current_state:
        await state.clear()
        await message.answer(
            "❌ Операция отменена.\n\n"
            "Выберите действие из меню.",
            reply_markup=get_parent_menu()
        )
    else:
        await message.answer("Нет активной операции для отмены.")
