from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import ICourseService, ISubscriptionService
from src.infrastructure.persistence.repositories import CityRepository, CategoryRepository
from src.presentation.keyboards.inline_keyboards import (
    get_search_params_keyboard,
    get_cities_keyboard,
    get_categories_keyboard,
    get_course_keyboard,
    get_course_detail_keyboard,
    get_tariff_keyboard
)
from src.presentation.states import SearchStates
from src.infrastructure.utils import generate_subscription_qr, generate_qr_code


router = Router()


@router.callback_query(F.data == "search_city")
async def select_city(
    callback: CallbackQuery,
    city_repo: FromDishka[CityRepository]
):
    cities = await city_repo.get_all_cities()
    
    await callback.message.edit_text(
        "🏙 Выбери город:",
        reply_markup=get_cities_keyboard(cities)
    )
    await callback.answer()


@router.callback_query(F.data == "search_category")
async def select_category(
    callback: CallbackQuery,
    category_repo: FromDishka[CategoryRepository]
):
    categories = await category_repo.get_all_categories()
    
    await callback.message.edit_text(
        "📂 Выбери категорию:",
        reply_markup=get_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data == "search_age")
async def select_age(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎂 Поиск по возрасту\n\n"
        "Введите возраст (например: 12):"
    )
    await state.set_state(SearchStates.waiting_for_age)
    await callback.answer()


@router.callback_query(F.data.startswith("city_"))
async def city_selected(
    callback: CallbackQuery,
    state: FSMContext,
    category_repo: FromDishka[CategoryRepository]
):
    city_id = int(callback.data.replace("city_", ""))
    await state.update_data(city=city_id)
    
    categories = await category_repo.get_all_categories()
    
    await callback.message.edit_text(
        "Город выбран\n\nВыбери категорию:",
        reply_markup=get_categories_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_selected(
    callback: CallbackQuery,
    state: FSMContext,
    course_service: FromDishka[ICourseService]
):
    category_id = int(callback.data.replace("category_", ""))
    data = await state.get_data()
    city_id = data.get("city")
    
    courses = await course_service.search_courses(
        city_id=city_id,
        category_id=category_id
    )
    
    if not courses:
        await callback.message.edit_text(
            "😔 Курсов не найдено. Попробуй другие параметры.",
            reply_markup=get_search_params_keyboard()
        )
        await callback.answer()
        return
    
    text = f"Найдено курсов: {len(courses)}\n\n"
    for course in courses[:5]:
        text += f"📘 Курс: {course.name}\n"
        text += f"🏫 {course.center.name if course.center else 'Не указано'}\n"
        text += f"📍 {course.center.city if course.center else ''}\n\n"
        
        await callback.message.answer(
            text,
            reply_markup=get_course_keyboard(course.id)
        )
        text = ""
    
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("course_detail_"))
async def course_detail(
    callback: CallbackQuery,
    course_service: FromDishka[ICourseService]
):
    course_id = int(callback.data.replace("course_detail_", ""))
    course = await course_service.get_course_by_id(course_id)
    
    if not course:
        await callback.answer("Курс не найден", show_alert=True)
        return
    
    text = f"📘 {course.name}\n\n"
    text += f"🏫 Центр: {course.center.name if course.center else 'Не указано'}\n"
    text += f"📍 {course.center.city if course.center else ''}\n\n"
    
    if course.description:
        text += f"📝 Описание:\n{course.description}\n\n"
    
    if course.schedule:
        text += f"🕒 Расписание:\n{course.schedule}\n\n"
    
    await callback.message.edit_text(text, reply_markup=get_course_detail_keyboard(course_id))
    await callback.answer()


@router.callback_query(F.data.startswith("buy_course_"))
async def buy_course(
    callback: CallbackQuery,
    course_service: FromDishka[ICourseService]
):
    try:
        course_id = int(callback.data.replace("buy_course_", ""))
        course = await course_service.get_course_by_id(course_id)
        
        if not course:
            await callback.answer("Курс не найден", show_alert=True)
            return
        
        text = "💎 Выбери тариф:\n\n"
        
        await callback.message.answer(
            text,
            reply_markup=get_tariff_keyboard(
                course_id,
                course.price_4,
                course.price_8,
                course.price_unlimited
            )
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in buy_course: {e}", exc_info=True)
        await callback.answer("Ошибка при покупке абонемента", show_alert=True)


@router.callback_query(F.data.startswith("tariff_"))
async def tariff_selected(
    callback: CallbackQuery,
    state: FSMContext,
    subscription_service: FromDishka[ISubscriptionService]
):
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("Ошибка: неверный формат данных", show_alert=True)
            return
        
        course_id = int(parts[1])
        tariff = parts[2]
        
        if tariff not in ["4", "8", "unlimited"]:
            await callback.answer("Ошибка: неверный тариф", show_alert=True)
            return
        
        user_id = callback.from_user.id
        
        subscription = await subscription_service.create_subscription_for_course(
            user_id=user_id,
            course_id=course_id,
            tariff=tariff
        )
        
        if not subscription:
            await callback.answer("Ошибка при создании абонемента", show_alert=True)
            return
        
        qr_id, qr_image = generate_subscription_qr(user_id, subscription.id)
        
        await subscription_service.update_qr_code(subscription.id, qr_id)
        
        await callback.message.answer(
            "🎉 Абонемент активирован!\n\n"
            "Вот твой QR-код для посещений 👇"
        )
        
        try:
            qr_bytes = qr_image.getvalue()
            await callback.message.answer_photo(
                photo=BufferedInputFile(qr_bytes, filename="qr_code.png"),
                caption="Твой QR-код для посещений"
            )
        except Exception:
            await callback.message.answer(
                f"QR-код создан!\nКод: {qr_id}\n\n"
                f"Установите Pillow для отображения QR-кода как изображения."
            )
        
        await callback.answer()
        await state.clear()
    except Exception as e:
        logger.error(f"Error in tariff_selected: {e}", exc_info=True)
        await callback.answer("Ошибка при выборе тарифа", show_alert=True)


@router.callback_query(F.data.startswith("show_qr_"))
async def show_qr(
    callback: CallbackQuery,
    subscription_service: FromDishka[ISubscriptionService]
):
    try:
        subscription_id = int(callback.data.replace("show_qr_", ""))
        user_id = callback.from_user.id
        
        subscriptions = await subscription_service.get_user_subscriptions(user_id)
        subscription = next((s for s in subscriptions if s.id == subscription_id), None)
        
        if not subscription:
            await callback.answer("Абонемент не найден", show_alert=True)
            return
        
        if not subscription.qr_code:
            await callback.answer("QR-код не найден", show_alert=True)
            return
        
        qr_image = generate_qr_code(subscription.qr_code)
        
        qr_bytes = qr_image.getvalue()
        await callback.message.answer_photo(
            photo=BufferedInputFile(qr_bytes, filename="qr_code.png"),
            caption="Твой QR-код для посещений"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in show_qr: {e}", exc_info=True)
        await callback.answer("Ошибка при показе QR-кода", show_alert=True)
