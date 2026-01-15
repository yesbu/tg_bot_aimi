from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dishka import FromDishka

from src.application.interfaces.services import ICourseService, ISubscriptionService
from src.presentation.bot.keyboards.inline_keyboards import (
    get_search_params_keyboard,
    get_course_keyboard,
    get_subscription_keyboard
)
from src.presentation.bot.states import SearchStates


router = Router()


@router.message(F.text == "📚 Каталог курсов")
async def catalog_menu(message: Message):
    await message.answer(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )


@router.message(SearchStates.waiting_for_age)
async def age_received(
    message: Message,
    state: FSMContext,
    course_service: FromDishka[ICourseService]
):
    try:
        age = int(message.text.strip())
        if age < 1 or age > 120:
            await message.answer("❌ Возраст должен быть от 1 до 120 лет.\n\nПопробуйте еще раз:")
            return
        
        data = await state.get_data()
        city = data.get("city")
        category = data.get("category")
        
        courses = await course_service.search_courses(
            city=city,
            category=category,
            age=age
        )
        
        if not courses:
            await message.answer(
                "😔 Курсов для этого возраста не найдено. Попробуйте другие параметры.",
                reply_markup=get_search_params_keyboard()
            )
            await state.clear()
            return
        
        text = f"Найдено курсов для возраста {age} лет: {len(courses)}\n\n"
        for course in courses[:5]:
            text += f"📘 Курс: {course.name}\n"
            text += f"🏫 {course.center.name if course.center else 'Не указано'}\n"
            text += f"📍 {course.center.city if course.center else ''}\n\n"
            
            await message.answer(
                text,
                reply_markup=get_course_keyboard(course.id)
            )
            text = ""
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Возраст должен быть числом.\n\nПопробуйте еще раз:")


@router.message(F.text == "🎫 Мои абонементы")
async def my_subscriptions(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "🎫 У тебя пока нет абонементов.\n\n"
            "Купи абонемент в каталоге курсов! 📚"
        )
        return
    
    for sub in subscriptions:
        remaining = sub.lessons_remaining if hasattr(sub, 'lessons_remaining') else 0
        text = f"🔹 Абонемент — осталось {remaining} занятий"
        await message.answer(text, reply_markup=get_subscription_keyboard(sub.id))


@router.message(F.text == "🕒 Расписание")
async def schedule(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "🕒 Расписание\n\n"
            "У тебя пока нет активных абонементов.\n"
            "Купи абонемент, чтобы увидеть расписание!"
        )
        return
    
    text = "🕒 Твое расписание:\n\n"
    
    for sub in subscriptions:
        if hasattr(sub, 'course') and sub.course:
            text += f"📘 {sub.course.name}\n"
            if hasattr(sub.course, 'schedule') and sub.course.schedule:
                text += f"   {sub.course.schedule}\n\n"
            else:
                text += f"   Расписание уточняется\n\n"
    
    if len(text) == len("🕒 Твое расписание:\n\n"):
        text += "Расписание для твоих курсов пока не установлено.\n"
        text += "Свяжись с центром для уточнения."
    
    await message.answer(text)


@router.message(F.text == "📊 Статистика")
async def statistics(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "📊 Статистика\n\n"
            "У тебя пока нет абонементов для отслеживания статистики."
        )
        return
    
    text = "📊 Твоя статистика:\n\n"
    
    total_visits = 0
    for sub in subscriptions:
        if hasattr(sub, 'course') and sub.course:
            text += f"📘 {sub.course.name}\n"
            
            lessons_total = 0
            if sub.tariff == "4":
                lessons_total = 4
            elif sub.tariff == "8":
                lessons_total = 8
            elif sub.tariff == "unlimited":
                lessons_total = 999
            
            remaining = sub.lessons_remaining if hasattr(sub, 'lessons_remaining') else lessons_total
            used = lessons_total - remaining if lessons_total != 999 else 0
            
            text += f"   Использовано: {used}\n"
            text += f"   Осталось: {remaining if lessons_total != 999 else '∞'}\n\n"
            
            total_visits += used
    
    text += f"\n🎯 Всего посещений: {total_visits}"
    
    await message.answer(text)


@router.message(F.text == "💳 Мои платежи")
async def my_payments(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "💳 История платежей\n\n"
            "У тебя пока нет платежей."
        )
        return
    
    text = "💳 История платежей:\n\n"
    
    for sub in subscriptions:
        if hasattr(sub, 'course') and sub.course:
            text += f"📘 {sub.course.name}\n"
            
            price = 0
            if sub.tariff == "4" and hasattr(sub.course, 'price_4'):
                price = sub.course.price_4
            elif sub.tariff == "8" and hasattr(sub.course, 'price_8'):
                price = sub.course.price_8
            elif sub.tariff == "unlimited" and hasattr(sub.course, 'price_unlimited'):
                price = sub.course.price_unlimited
            
            text += f"   Тариф: {sub.tariff} занятий\n"
            text += f"   Сумма: {price} ₸\n"
            
            if hasattr(sub, 'created_at'):
                text += f"   Дата: {sub.created_at.strftime('%d.%m.%Y')}\n"
            
            text += f"   Статус: ✅ Оплачено\n\n"
    
    await message.answer(text)


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message):
    await message.answer(
        "🆘 Поддержка\n\n"
        "Если у тебя есть вопросы, напиши нам:\n"
        "📧 support@example.com\n"
        "📱 +7 (XXX) XXX-XX-XX"
    )
