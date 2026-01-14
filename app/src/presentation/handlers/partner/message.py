from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import ICenterService, IUserService, ISubscriptionService
from src.infrastructure.persistence.repositories import CityRepository, CategoryRepository
from src.presentation.keyboards.inline_keyboards import get_cities_keyboard, get_categories_keyboard
from src.presentation.states.partner_states import PartnerRegistrationStates, CourseManagementStates, TeacherManagementStates


router = Router()


@router.message(F.text == "🏢 Мой центр")
async def my_center(
    message: Message,
    center_service: FromDishka[ICenterService]
):
    partner_id = message.from_user.id
    centers = await center_service.get_partner_centers(partner_id)
    
    if not centers:
        await message.answer(
            "🏢 У тебя пока нет зарегистрированных центров.\n\n"
            "Нажми '➕ Зарегистрировать центр' чтобы начать!"
        )
        return
    
    for center in centers:
        status_emoji = "✅" if center.status.value == "approved" else "⏳" if center.status.value == "pending" else "❌"
        text = f"{status_emoji} **{center.name}**\n"
        text += f"📍 {center.city}\n"
        text += f"📞 {center.phone or 'Не указан'}\n"
        text += f"Статус: {center.status.value}\n"
        
        await message.answer(text)


@router.message(F.text == "➕ Зарегистрировать центр")
async def register_center_start(message: Message, state: FSMContext):
    await message.answer(
        "🏢 Регистрация центра\n\n"
        "Введи название центра:"
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_center_name)


@router.message(PartnerRegistrationStates.waiting_for_center_name)
async def center_name_received(
    message: Message,
    state: FSMContext,
    city_repo: FromDishka[CityRepository]
):
    name = message.text.strip()
    
    if len(name) < 3 or len(name) > 100:
        await message.answer(
            "❌ Название должно быть от 3 до 100 символов.\n\n"
            "Попробуй еще раз:"
        )
        return
    
    await state.update_data(center_name=name)
    
    cities = await city_repo.get_all_cities()
    
    await message.answer(
        f"Отлично! Теперь выбери город:",
        reply_markup=get_cities_keyboard(cities)
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_center_city)


@router.message(PartnerRegistrationStates.waiting_for_center_address)
async def center_address_received(message: Message, state: FSMContext):
    address = message.text.strip()
    
    if len(address) < 5:
        await message.answer(
            "❌ Адрес слишком короткий.\n\n"
            "Попробуй еще раз:"
        )
        return
    
    await state.update_data(center_address=address)
    await message.answer("Введи номер телефона центра:")
    await state.set_state(PartnerRegistrationStates.waiting_for_center_phone)


@router.message(PartnerRegistrationStates.waiting_for_center_phone)
async def center_phone_received(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    await state.update_data(center_phone=phone)
    await message.answer(
        "Введи описание центра (или отправь '-' чтобы пропустить):"
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_center_description)


@router.message(PartnerRegistrationStates.waiting_for_center_description)
async def center_description_received(
    message: Message,
    state: FSMContext,
    center_service: FromDishka[ICenterService]
):
    description = message.text.strip()
    if description == "-":
        description = None
    
    data = await state.get_data()
    partner_id = message.from_user.id
    
    try:
        center = await center_service.create_center(
            partner_id=partner_id,
            name=data["center_name"],
            city=data["center_city_name"],
            address=data["center_address"],
            phone=data["center_phone"],
            description=description
        )
        
        await message.answer(
            f"✅ Центр '{center.name}' успешно зарегистрирован!\n\n"
            "Статус: ⏳ На модерации\n\n"
            "Администратор проверит данные и одобрит центр."
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error creating center: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при регистрации центра. Попробуй позже."
        )
        await state.clear()


@router.message(F.text == "👨‍🏫 Преподаватели")
async def teachers_menu(
    message: Message,
    center_service: FromDishka[ICenterService]
):
    partner_id = message.from_user.id
    centers = await center_service.get_partner_centers(partner_id)
    
    if not centers:
        await message.answer(
            "❌ У тебя пока нет зарегистрированных центров.\n\n"
            "Сначала зарегистрируй центр!"
        )
        return
    
    approved_centers = [c for c in centers if c.status.value == "approved"]
    
    if not approved_centers:
        await message.answer(
            "⏳ Твой центр еще на модерации.\n\n"
            "Дождись одобрения администратора."
        )
        return
    
    await message.answer(
        "👨‍🏫 Управление преподавателями\n\n"
        "Используй кнопки меню для управления преподавателями.\n\n"
        "Функции:\n"
        "• Добавить преподавателя\n"
        "• Просмотр списка\n"
        "• Редактирование данных"
    )


@router.message(F.text == "📚 Курсы")
async def courses_menu(
    message: Message,
    center_service: FromDishka[ICenterService]
):
    partner_id = message.from_user.id
    centers = await center_service.get_partner_centers(partner_id)
    
    if not centers:
        await message.answer(
            "❌ У тебя пока нет зарегистрированных центров.\n\n"
            "Сначала зарегистрируй центр!"
        )
        return
    
    approved_centers = [c for c in centers if c.status.value == "approved"]
    
    if not approved_centers:
        await message.answer(
            "⏳ Твой центр еще на модерации.\n\n"
            "Дождись одобрения администратора."
        )
        return
    
    await message.answer(
        "📚 Управление курсами\n\n"
        "Используй кнопки меню для управления курсами.\n\n"
        "Функции:\n"
        "• Добавить курс\n"
        "• Просмотр списка\n"
        "• Редактирование\n"
        "• Установка цен"
    )


@router.message(F.text == "📷 Сканировать QR")
async def scan_qr_start(message: Message):
    await message.answer(
        "📷 Сканирование QR-кода\n\n"
        "Отправь фото QR-кода или введи код вручную:"
    )


@router.message(F.photo)
async def qr_photo_received(message: Message):
    await message.answer(
        "📷 Фото получено!\n\n"
        "Функция распознавания QR-кода в разработке.\n"
        "Пока введи код вручную."
    )


@router.message(F.text.regexp(r'^[A-Z0-9]{8,}$'))
async def qr_code_received(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    qr_code = message.text.strip()
    
    try:
        subscription = await subscription_service.get_by_qr_code(qr_code)
        
        if not subscription:
            await message.answer(
                "❌ QR-код не найден.\n\n"
                "Проверь правильность кода."
            )
            return
        
        if subscription.lessons_remaining <= 0:
            await message.answer(
                "❌ Абонемент исчерпан!\n\n"
                f"Осталось занятий: 0"
            )
            return
        
        await subscription_service.mark_visit(subscription.id)
        
        remaining = subscription.lessons_remaining - 1
        
        await message.answer(
            f"✅ Посещение отмечено!\n\n"
            f"Абонемент: {subscription.course.name if hasattr(subscription, 'course') and subscription.course else 'N/A'}\n"
            f"Осталось занятий: {remaining}"
        )
    except Exception as e:
        logger.error(f"Error processing QR code: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при обработке QR-кода."
        )


@router.message(F.text == "📊 Аналитика")
async def analytics(
    message: Message,
    center_service: FromDishka[ICenterService],
    subscription_service: FromDishka[ISubscriptionService]
):
    partner_id = message.from_user.id
    centers = await center_service.get_partner_centers(partner_id)
    
    if not centers:
        await message.answer(
            "❌ У тебя пока нет зарегистрированных центров."
        )
        return
    
    text = "📊 Аналитика по центрам:\n\n"
    
    for center in centers:
        text += f"🏢 {center.name}\n"
        text += f"Статус: {center.status.value}\n"
        
        if center.status.value == "approved":
            text += f"📈 Активных курсов: N/A\n"
            text += f"👥 Студентов: N/A\n"
            text += f"💰 Доход: N/A\n"
        
        text += "\n"
    
    text += "\n💡 Полная аналитика в разработке."
    
    await message.answer(text)
