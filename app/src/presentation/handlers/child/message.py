from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from dishka import FromDishka
from loguru import logger

from src.application.interfaces.services import ISubscriptionService
from src.infrastructure.utils import generate_qr_code


router = Router()


@router.message(F.text == "🎫 Мой QR-код")
async def my_qr_code(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "🎫 У тебя пока нет активных абонементов.\n\n"
            "Попроси родителей купить абонемент!"
        )
        return
    
    for sub in subscriptions:
        if not sub.qr_code:
            continue
        
        try:
            qr_image = generate_qr_code(sub.qr_code)
            qr_bytes = qr_image.getvalue()
            
            course_name = sub.course.name if hasattr(sub, 'course') and sub.course else "Абонемент"
            
            await message.answer_photo(
                photo=BufferedInputFile(qr_bytes, filename="qr_code.png"),
                caption=f"🎫 {course_name}\n\nПокажи этот QR-код преподавателю"
            )
        except Exception as e:
            logger.error(f"Error generating QR code: {e}", exc_info=True)
            await message.answer(
                f"QR-код: {sub.qr_code}\n\n"
                f"Покажи этот код преподавателю"
            )


@router.message(F.text == "📅 Расписание")
async def schedule(
    message: Message,
    subscription_service: FromDishka[ISubscriptionService]
):
    user_id = message.from_user.id
    subscriptions = await subscription_service.get_user_subscriptions(user_id)
    
    if not subscriptions:
        await message.answer(
            "📅 Расписание\n\n"
            "У тебя пока нет активных абонементов.\n"
            "Попроси родителей купить абонемент!"
        )
        return
    
    text = "📅 Твое расписание:\n\n"
    
    for sub in subscriptions:
        if hasattr(sub, 'course') and sub.course:
            text += f"📘 {sub.course.name}\n"
            if hasattr(sub.course, 'schedule') and sub.course.schedule:
                text += f"   {sub.course.schedule}\n\n"
            else:
                text += f"   Расписание уточняется\n\n"
    
    if len(text) == len("📅 Твое расписание:\n\n"):
        text += "Расписание для твоих курсов пока не установлено.\n"
        text += "Спроси у родителей или преподавателя."
    
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
