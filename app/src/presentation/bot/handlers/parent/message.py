from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.services.child_service import ChildService
from src.application.interfaces.services import ISubscriptionService
from src.presentation.bot.keyboards.inline_keyboards import get_children_keyboard
from src.presentation.bot.states.parent_states import ParentStates


router = Router()


@router.message(F.text == "👶 Мои дети")
async def my_children(
    message: Message,
    child_service: FromDishka[ChildService]
):
    parent_id = message.from_user.id
    children = await child_service.get_parent_children(parent_id)
    
    if not children:
        await message.answer(
            "👶 У тебя пока нет добавленных детей.\\n\\n"
            "Нажми '➕ Добавить ребенка' чтобы добавить!"
        )
        return
    
    text = "👶 Твои дети:\\n\\n"
    for child in children:
        text += f"• {child.name}, {child.age} лет\\n"
    
    await message.answer(text)


@router.message(F.text == "➕ Добавить ребенка")
async def add_child_start(message: Message, state: FSMContext):
    await message.answer(
        "👶 Добавление ребенка\\n\\n"
        "Введи имя ребенка:"
    )
    await state.set_state(ParentStates.waiting_for_child_name)


@router.message(ParentStates.waiting_for_child_name)
async def child_name_received(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer(
            "❌ Имя должно быть от 2 до 50 символов.\\n\\n"
            "Попробуй еще раз:"
        )
        return
    
    await state.update_data(child_name=name)
    await message.answer(
        f"Отлично! Теперь введи возраст {name}:"
    )
    await state.set_state(ParentStates.waiting_for_child_age)


@router.message(ParentStates.waiting_for_child_age)
async def child_age_received(
    message: Message,
    state: FSMContext,
    child_service: FromDishka[ChildService]
):
    try:
        age = int(message.text.strip())
        
        if age < 1 or age > 18:
            await message.answer(
                "❌ Возраст должен быть от 1 до 18 лет.\\n\\n"
                "Попробуй еще раз:"
            )
            return
        
        data = await state.get_data()
        name = data.get("child_name")
        parent_id = message.from_user.id
        
        child = await child_service.create_child(
            parent_id=parent_id,
            name=name,
            age=age
        )
        
        await message.answer(
            f"✅ Ребенок {name} ({age} лет) успешно добавлен!"
        )
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Возраст должен быть числом.\\n\\n"
            "Попробуй еще раз:"
        )


@router.message(F.text == "🎫 Купить абонемент для ребенка")
async def buy_subscription_for_child(
    message: Message,
    state: FSMContext,
    child_service: FromDishka[ChildService]
):
    parent_id = message.from_user.id
    children = await child_service.get_parent_children(parent_id)
    
    if not children:
        await message.answer(
            "❌ У тебя пока нет добавленных детей.\\n\\n"
            "Сначала добавь ребенка через '➕ Добавить ребенка'"
        )
        return
    
    await message.answer(
        "Выбери ребенка:",
        reply_markup=get_children_keyboard(children)
    )
    await state.set_state(ParentStates.selecting_child_for_subscription)
