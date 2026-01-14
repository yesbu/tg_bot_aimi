from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from dishka import FromDishka
from loguru import logger

from src.application.services.child_service import ChildService
from src.application.interfaces.services import ICourseService, ISubscriptionService
from src.infrastructure.persistence.repositories import CityRepository, CategoryRepository
from src.presentation.keyboards.inline_keyboards import (
    get_search_params_keyboard,
    get_cities_keyboard,
    get_categories_keyboard,
    get_course_keyboard,
    get_tariff_keyboard
)
from src.presentation.states import SearchStates
from src.infrastructure.utils import generate_subscription_qr


router = Router()


@router.callback_query(F.data.startswith("select_child_"))
async def child_selected_for_subscription(
    callback: CallbackQuery,
    state: FSMContext,
    child_service: FromDishka[ChildService],
    city_repo: FromDishka[CityRepository]
):
    child_id = int(callback.data.replace("select_child_", ""))
    child = await child_service.get_child_by_id(child_id)
    
    if not child:
        await callback.answer("Ребенок не найден", show_alert=True)
        return
    
    await state.update_data(selected_child_id=child_id)
    
    cities = await city_repo.get_all_cities()
    
    await callback.message.edit_text(
        f"Покупка абонемента для {child.name}\n\n"
        "🏙 Выбери город:",
        reply_markup=get_cities_keyboard(cities)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("city_"))
async def city_selected_for_child(
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
async def category_selected_for_child(
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


@router.callback_query(F.data.startswith("tariff_child_"))
async def tariff_selected_for_child(
    callback: CallbackQuery,
    state: FSMContext,
    subscription_service: FromDishka[ISubscriptionService],
    child_service: FromDishka[ChildService]
):
    try:
        parts = callback.data.split("_")
        if len(parts) < 4:
            await callback.answer("Ошибка: неверный формат данных", show_alert=True)
            return
        
        course_id = int(parts[2])
        tariff = parts[3]
        
        data = await state.get_data()
        child_id = data.get("selected_child_id")
        
        if not child_id:
            await callback.answer("Ошибка: ребенок не выбран", show_alert=True)
            return
        
        child = await child_service.get_child_by_id(child_id)
        parent_id = callback.from_user.id
        
        subscription = await subscription_service.create_subscription_for_course(
            user_id=parent_id,
            course_id=course_id,
            tariff=tariff,
            child_id=child_id
        )
        
        if not subscription:
            await callback.answer("Ошибка при создании абонемента", show_alert=True)
            return
        
        qr_id, qr_image = generate_subscription_qr(parent_id, subscription.id)
        
        await subscription_service.update_qr_code(subscription.id, qr_id)
        
        await callback.message.answer(
            f"🎉 Абонемент для {child.name} активирован!\n\n"
            "Вот QR-код для посещений 👇"
        )
        
        try:
            qr_bytes = qr_image.getvalue()
            await callback.message.answer_photo(
                photo=BufferedInputFile(qr_bytes, filename="qr_code.png"),
                caption=f"QR-код для {child.name}"
            )
        except Exception:
            await callback.message.answer(
                f"QR-код создан!\nКод: {qr_id}\n\n"
                f"Установите Pillow для отображения QR-кода как изображения."
            )
        
        await callback.answer()
        await state.clear()
    except Exception as e:
        logger.error(f"Error in tariff_selected_for_child: {e}", exc_info=True)
        await callback.answer("Ошибка при выборе тарифа", show_alert=True)


@router.callback_query(F.data == "back_to_parent_menu")
async def back_to_parent_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer()
