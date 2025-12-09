import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from utils.keyboards import (
    get_main_menu, get_search_params_keyboard, get_cities_keyboard,
    get_categories_keyboard, get_course_keyboard, get_course_detail_keyboard,
    get_tariff_keyboard, get_payment_keyboard, get_subscription_keyboard
)
from utils.qr_generator import generate_subscription_qr
from config import ROLE_USER

logger = logging.getLogger(__name__)

router = Router()
db = Database()


class SearchStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_age = State()


@router.message(F.text == "📚 Каталог курсов")
async def catalog_menu(message: Message):
    """Показывает меню поиска курсов"""
    await message.answer(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )


@router.callback_query(F.data == "search_city")
async def select_city(callback: CallbackQuery):
    """Выбор города"""
    await callback.message.edit_text(
        "🏙 Выбери город:",
        reply_markup=get_cities_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "search_category")
async def select_category(callback: CallbackQuery):
    """Выбор категории"""
    await callback.message.edit_text(
        "📂 Выбери категорию:",
        reply_markup=get_categories_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "search_price")
async def select_price(callback: CallbackQuery, state: FSMContext):
    """Поиск по цене"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "💰 Поиск по цене\n\n"
        "Выберите диапазон цены:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 До 10,000 ₸", callback_data="price_range_0_10000")],
            [InlineKeyboardButton(text="💰 10,000 - 25,000 ₸", callback_data="price_range_10000_25000")],
            [InlineKeyboardButton(text="💰 25,000 - 50,000 ₸", callback_data="price_range_25000_50000")],
            [InlineKeyboardButton(text="💰 От 50,000 ₸", callback_data="price_range_50000_999999")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price_range_"))
async def price_range_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора диапазона цены"""
    try:
        # Формат: price_range_{min}_{max}
        parts = callback.data.replace("price_range_", "").split("_")
        price_min = int(parts[0])
        price_max = int(parts[1])
        
        data = await state.get_data()
        city = data.get("city")
        category = data.get("category")
        
        # Получаем курсы
        courses = await db.get_courses(city=city, category=category)
        
        # Фильтруем по цене
        filtered_courses = []
        for course in courses:
            price_8 = course.get("price_8", 0)
            if price_min <= price_8 <= price_max:
                filtered_courses.append(course)
        
        if not filtered_courses:
            await callback.message.edit_text(
                "😔 Курсов в этом диапазоне цен не найдено.",
                reply_markup=get_search_params_keyboard()
            )
            await callback.answer()
            return
        
        # Показываем курсы
        text = f"Найдено курсов: {len(filtered_courses)}\n\n"
        for course in filtered_courses[:5]:
            center_name = course.get("center_name", "Не указано")
            price_8 = course.get("price_8", 0)
            rating = course.get("rating", 0)
            address = course.get("address", "")
            city_name = course.get("city", "")
            
            text += f"📘 Курс: {course['name']}\n"
            text += f"🏫 {center_name}\n"
            text += f"⭐️ Рейтинг: {rating}\n"
            text += f"📍 {city_name}, {address}\n\n"
            
            await callback.message.answer(
                text,
                reply_markup=get_course_keyboard(course["course_id"])
            )
            text = ""
        
        await callback.answer()
        await state.clear()
    except (ValueError, IndexError):
        await callback.answer("Ошибка: неверный формат", show_alert=True)


@router.callback_query(F.data == "search_age")
async def select_age(callback: CallbackQuery, state: FSMContext):
    """Поиск по возрасту"""
    await callback.message.edit_text(
        "🎂 Поиск по возрасту\n\n"
        "Введите возраст (например: 12):"
    )
    await state.set_state(SearchStates.waiting_for_age)
    await callback.answer()


@router.message(SearchStates.waiting_for_age)
async def age_received(message: Message, state: FSMContext):
    """Обработка возраста для поиска"""
    try:
        age = int(message.text.strip())
        if age < 1 or age > 120:
            await message.answer("❌ Возраст должен быть от 1 до 120 лет.\n\nПопробуйте еще раз:")
            return
        
        data = await state.get_data()
        city = data.get("city")
        category = data.get("category")
        
        # Получаем курсы с фильтрацией по возрасту
        courses = await db.get_courses(city=city, category=category, age=age)
        
        if not courses:
            await message.answer(
                "😔 Курсов для этого возраста не найдено. Попробуйте другие параметры.",
                reply_markup=get_search_params_keyboard()
            )
            await state.clear()
            return
        
        # Показываем курсы
        text = f"Найдено курсов для возраста {age} лет: {len(courses)}\n\n"
        for course in courses[:5]:
            center_name = course.get("center_name", "Не указано")
            price_8 = course.get("price_8", 0)
            rating = course.get("rating", 0)
            address = course.get("address", "")
            city_name = course.get("city", "")
            
            text += f"📘 Курс: {course['name']}\n"
            text += f"🏫 {center_name}\n"
            text += f"⭐️ Рейтинг: {rating}\n"
            text += f"📍 {city_name}, {address}\n\n"
            
            await message.answer(
                text,
                reply_markup=get_course_keyboard(course["course_id"])
            )
            text = ""
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Возраст должен быть числом.\n\nПопробуйте еще раз:")


@router.callback_query(F.data == "search_rating")
async def select_rating(callback: CallbackQuery, state: FSMContext):
    """Поиск по рейтингу"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await callback.message.edit_text(
        "⭐ Поиск по рейтингу\n\n"
        "Выберите минимальный рейтинг:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 4.0+", callback_data="min_rating_4"),
             InlineKeyboardButton(text="⭐⭐ 4.5+", callback_data="min_rating_4.5")],
            [InlineKeyboardButton(text="⭐⭐⭐ 4.7+", callback_data="min_rating_4.7"),
             InlineKeyboardButton(text="⭐⭐⭐⭐ 4.9+", callback_data="min_rating_4.9")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_search")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("min_rating_"))
async def min_rating_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора минимального рейтинга"""
    try:
        min_rating = float(callback.data.replace("min_rating_", ""))
        
        data = await state.get_data()
        city = data.get("city")
        category = data.get("category")
        
        # Получаем курсы
        courses = await db.get_courses(city=city, category=category)
        
        # Фильтруем по рейтингу
        filtered_courses = [c for c in courses if c.get("rating", 0) >= min_rating]
        
        if not filtered_courses:
            await callback.message.edit_text(
                f"😔 Курсов с рейтингом {min_rating}+ не найдено.",
                reply_markup=get_search_params_keyboard()
            )
            await callback.answer()
            return
        
        # Показываем курсы
        text = f"Найдено курсов с рейтингом {min_rating}+: {len(filtered_courses)}\n\n"
        for course in filtered_courses[:5]:
            center_name = course.get("center_name", "Не указано")
            price_8 = course.get("price_8", 0)
            rating = course.get("rating", 0)
            address = course.get("address", "")
            city_name = course.get("city", "")
            
            text += f"📘 Курс: {course['name']}\n"
            text += f"🏫 {center_name}\n"
            text += f"⭐️ Рейтинг: {rating}\n"
            text += f"📍 {city_name}, {address}\n\n"
            
            await callback.message.answer(
                text,
                reply_markup=get_course_keyboard(course["course_id"])
            )
            text = ""
        
        await callback.answer()
        await state.clear()
    except ValueError:
        await callback.answer("Ошибка: неверный формат", show_alert=True)


@router.callback_query(F.data.startswith("city_"))
async def city_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора города"""
    city = callback.data.replace("city_", "")
    await state.update_data(city=city)
    
    await callback.message.edit_text(
        f"Город: {city}\n\nВыбери категорию:",
        reply_markup=get_categories_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории и показ курсов"""
    category = callback.data.replace("category_", "")
    data = await state.get_data()
    city = data.get("city")
    
    # Получаем курсы
    courses = await db.get_courses(city=city, category=category)
    
    if not courses:
        await callback.message.edit_text(
            "😔 Курсов не найдено. Попробуй другие параметры.",
            reply_markup=get_search_params_keyboard()
        )
        await callback.answer()
        return
    
    # Показываем первые 5 курсов
    text = f"Найдено курсов: {len(courses)}\n\n"
    for course in courses[:5]:
        center_name = course.get("center_name", "Не указано")
        price_8 = course.get("price_8", 0)
        rating = course.get("rating", 0)
        address = course.get("address", "")
        city_name = course.get("city", "")
        
        text += f"📘 Курс: {course['name']}\n"
        text += f"🏫 {center_name}\n"
        text += f"⭐️ Рейтинг: {rating}\n"
        text += f"📍 {city_name}, {address}\n\n"
        
        await callback.message.answer(
            text,
            reply_markup=get_course_keyboard(course["course_id"])
        )
        text = ""
    
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: CallbackQuery, state: FSMContext):
    """Возврат к параметрам поиска"""
    await state.clear()
    await callback.message.edit_text(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery, state: FSMContext):
    """Возврат к каталогу"""
    await state.clear()
    await callback.message.edit_text(
        "Выбери параметры поиска:",
        reply_markup=get_search_params_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reviews_"))
async def show_reviews(callback: CallbackQuery):
    """Показ отзывов о курсе"""
    try:
        course_id = int(callback.data.replace("reviews_", ""))
        course = await db.get_course(course_id)
        
        if not course:
            await callback.answer("Курс не найден", show_alert=True)
            return
        
        # Получаем отзывы из БД
        reviews = await db.get_reviews(course_id)
        user_id = callback.from_user.id
        user_review = await db.get_user_review(course_id, user_id)
        
        text = f"💬 Отзывы о курсе \"{course.get('name', 'Курс')}\"\n\n"
        
        if not reviews:
            text += "Пока отзывов нет. Будьте первым, кто оставит отзыв! ⭐"
        else:
            text += f"Всего отзывов: {len(reviews)}\n"
            text += f"⭐ Средний рейтинг: {course.get('rating', 0)}\n\n"
            
            for review in reviews[:10]:  # Показываем последние 10
                rating = review.get('rating', 0)
                stars = "⭐" * rating
                author = review.get('full_name') or review.get('username') or "Аноним"
                comment = review.get('comment', '')
                created_at = review.get('created_at', '')
                
                text += f"{stars} {author}\n"
                if comment:
                    text += f"   {comment[:100]}{'...' if len(comment) > 100 else ''}\n"
                if created_at:
                    try:
                        from datetime import datetime
                        if isinstance(created_at, str):
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            date_obj = created_at
                        date_str = date_obj.strftime('%d.%m.%Y')
                        text += f"   📅 {date_str}\n"
                    except:
                        pass
                text += "\n"
        
        from utils.keyboards import get_review_keyboard
        can_add = not user_review  # Можно добавить, если еще не оставлял отзыв
        await callback.message.answer(
            text,
            reply_markup=get_review_keyboard(course_id, can_add)
        )
        await callback.answer()
    except (ValueError, AttributeError):
        await callback.answer("Ошибка: неверный ID курса", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при получении отзывов: {e}", exc_info=True)
        await callback.answer("Ошибка при получении отзывов", show_alert=True)


@router.callback_query(F.data.startswith("extend_"))
async def extend_subscription(callback: CallbackQuery):
    """Продление абонемента"""
    try:
        subscription_id = int(callback.data.replace("extend_", ""))
        user_id = callback.from_user.id
        
        # Проверяем, что абонемент принадлежит пользователю
        subscriptions = await db.get_user_subscriptions(user_id)
        subscription = next((s for s in subscriptions if s.get("subscription_id") == subscription_id), None)
        
        if not subscription:
            await callback.answer("Абонемент не найден", show_alert=True)
            return
        
        course_id = subscription.get("course_id")
        course = await db.get_course(course_id) if course_id else None
        
        if not course:
            await callback.answer("Курс не найден", show_alert=True)
            return
        
        await callback.message.answer(
            f"🔄 Продление абонемента\n\n"
            f"Курс: {subscription.get('course_name', 'Курс')}\n\n"
            f"Выбери новый тариф:",
            reply_markup=get_tariff_keyboard(
                course_id,
                course.get("price_4"),
                course.get("price_8"),
                course.get("price_unlimited")
            )
        )
        await callback.answer()
    except (ValueError, AttributeError):
        await callback.answer("Ошибка: неверный ID абонемента", show_alert=True)


@router.callback_query(F.data.startswith("history_"))
async def subscription_history(callback: CallbackQuery):
    """История посещений абонемента"""
    try:
        subscription_id = int(callback.data.replace("history_", ""))
        user_id = callback.from_user.id
        
        # Получаем историю посещений
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("""
                SELECT v.*, c.name as center_name
                FROM visits v
                LEFT JOIN centers c ON v.center_id = c.center_id
                WHERE v.subscription_id = ?
                ORDER BY v.visited_at DESC
                LIMIT 20
            """, (subscription_id,)) as cursor:
                visits = await cursor.fetchall()
        
        if not visits:
            await callback.message.answer("📜 История посещений пуста.")
            await callback.answer()
            return
        
        text = "📜 История посещений:\n\n"
        for visit in visits:
            visit_date = visit.get("visited_at", "")
            center_name = visit.get("center_name", "Неизвестно")
            
            if visit_date:
                try:
                    from datetime import datetime
                    if isinstance(visit_date, str):
                        date_obj = datetime.fromisoformat(visit_date.replace('Z', '+00:00'))
                    else:
                        date_obj = visit_date
                    date_str = date_obj.strftime('%d.%m.%Y %H:%M')
                except:
                    date_str = str(visit_date)[:16]
            else:
                date_str = "Неизвестно"
            
            text += f"📅 {date_str}\n"
            text += f"🏫 {center_name}\n\n"
        
        await callback.message.answer(text)
        await callback.answer()
    except (ValueError, AttributeError):
        await callback.answer("Ошибка: неверный ID абонемента", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}", exc_info=True)
        await callback.answer("Ошибка при получении истории", show_alert=True)


@router.callback_query(F.data.startswith("course_detail_"))
async def course_detail(callback: CallbackQuery):
    """Детальная информация о курсе"""
    course_id = int(callback.data.replace("course_detail_", ""))
    course = await db.get_course(course_id)
    
    if not course:
        await callback.answer("Курс не найден", show_alert=True)
        return
    
    text = f"📘 {course['name']}\n\n"
    text += f"🏫 Центр: {course.get('center_name', 'Не указано')}\n"
    text += f"📍 {course.get('city', '')}, {course.get('address', '')}\n\n"
    
    if course.get("description"):
        text += f"📝 Описание:\n{course['description']}\n\n"
    
    if course.get("schedule"):
        text += f"🕒 Расписание:\n{course['schedule']}\n\n"
    
    if course.get("requirements"):
        text += f"📋 Требования:\n{course['requirements']}\n\n"
    
    if course.get("age_min") or course.get("age_max"):
        age_text = ""
        if course.get("age_min"):
            age_text += f"от {course['age_min']}"
        if course.get("age_max"):
            if age_text:
                age_text += " "
            age_text += f"до {course['age_max']}"
        text += f"🎂 Возраст: {age_text}\n\n"
    
    text += f"⭐️ Рейтинг: {course.get('rating', 0)}\n"
    
    await callback.message.edit_text(text, reply_markup=get_course_detail_keyboard(course_id))
    await callback.answer()


@router.callback_query(F.data.startswith("buy_template_"))
async def buy_template(callback: CallbackQuery, state: FSMContext):
    """Покупка универсального абонемента из шаблона"""
    try:
        template_id = int(callback.data.replace("buy_template_", ""))
        template = await db.get_subscription_template(template_id)
        
        if not template:
            await callback.answer("Абонемент не найден", show_alert=True)
            return
        
        if not template.get("is_active"):
            await callback.answer("Этот абонемент временно недоступен", show_alert=True)
            return
        
        user_id = callback.from_user.id
        price = template.get("price", 0)
        
        # Сохраняем данные покупки
        await state.update_data(
            template_id=template_id,
            price=price
        )
        
        # Создаём временный абонемент для платежа
        import uuid
        temp_qr_id = str(uuid.uuid4())
        subscription_id = await db.create_subscription(user_id, template_id, temp_qr_id)
        
        if not subscription_id:
            await callback.answer("Ошибка при создании абонемента", show_alert=True)
            return
        
        # Инициализируем платежный сервис
        try:
            from services.payment import AirbaPayClient, PaymentService
            from config import (
                AIRBA_PAY_BASE_URL, AIRBA_PAY_USER, AIRBA_PAY_PASSWORD,
                AIRBA_PAY_TERMINAL_ID, AIRBA_PAY_COMPANY_ID, AIRBA_PAY_WEBHOOK_URL
            )
            
            # Проверяем наличие настроек
            if not AIRBA_PAY_USER or not AIRBA_PAY_PASSWORD or not AIRBA_PAY_TERMINAL_ID:
                # Если платежная система не настроена, создаём абонемент без оплаты
                qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
                import aiosqlite
                async with aiosqlite.connect(db.db_path) as db_conn:
                    await db_conn.execute(
                        "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                        (qr_id, subscription_id)
                    )
                    await db_conn.commit()
                
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
                return
            
            # Создаём платеж
            client = AirbaPayClient(
                base_url=AIRBA_PAY_BASE_URL,
                user=AIRBA_PAY_USER,
                password=AIRBA_PAY_PASSWORD,
                terminal_id=AIRBA_PAY_TERMINAL_ID,
                company_id=AIRBA_PAY_COMPANY_ID
            )
            
            payment_service = PaymentService(client, db, AIRBA_PAY_WEBHOOK_URL)
            
            # Получаем данные пользователя
            user = await db.get_user(user_id)
            phone = user.get("phone", "") if user else ""
            email = ""  # У пользователя может не быть email
            
            payment_result = await payment_service.create_payment(
                user_id=user_id,
                subscription_id=subscription_id,
                amount=float(price),
                currency="KZT",
                description=f"Оплата абонемента: {template.get('name', 'Абонемент')}",
                language="ru",
                phone=phone,
                email=email
            )
            
            if not payment_result.get("success"):
                error_msg = payment_result.get("error", "Ошибка при создании платежа")
                await callback.message.answer(
                    f"❌ Ошибка при создании платежа:\n{error_msg}\n\n"
                    "Попробуйте позже или обратитесь в поддержку."
                )
                await callback.answer()
                return
            
            # Сохраняем payment_id в state для отслеживания
            await state.update_data(
                subscription_id=subscription_id,
                payment_id=payment_result.get("payment_id")
            )
            
            redirect_url = payment_result.get("redirect_url")
            
            if redirect_url:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                await callback.message.answer(
                    f"💳 Оплата абонемента\n\n"
                    f"Абонемент: {template.get('name', 'Абонемент')}\n"
                    f"Сумма: {price:,.0f} ₸\n\n"
                    f"Перейдите по ссылке для оплаты:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💳 Оплатить", url=redirect_url)],
                        [InlineKeyboardButton(text="✅ Проверить платеж", callback_data=f"check_payment_{payment_result.get('payment_id')}")],
                        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_payment_{subscription_id}")]
                    ])
                )
            else:
                await callback.message.answer(
                    "⚠️ Ссылка на оплату не получена. Обратитесь в поддержку."
                )
            
        except ImportError:
            # Если платежный сервис не настроен, создаём абонемент без оплаты
            qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as db_conn:
                await db_conn.execute(
                    "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                    (qr_id, subscription_id)
                )
                await db_conn.commit()
            
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
            await state.clear()
        
        await callback.answer()
    except (ValueError, Exception) as e:
        logger.error(f"Ошибка при покупке абонемента: {e}", exc_info=True)
        await callback.answer("Ошибка при покупке абонемента", show_alert=True)


@router.callback_query(F.data.startswith("buy_course_"))
async def buy_course(callback: CallbackQuery):
    """Покупка абонемента из каталога курсов - показываем тарифы"""
    try:
        course_id = int(callback.data.replace("buy_course_", ""))
        
        # Показываем тарифы
        text = "💎 Наши тарифы:\n\n"
        text += "📅 3 МЕСЯЦА\n"
        text += "• 195.000 ₸\n"
        text += "• 70.000 ₸/мес\n"
        text += "• +30 посещений\n\n"
        text += "📅 6 МЕСЯЦЕВ\n"
        text += "• 300.000 ₸\n"
        text += "• 55.000 ₸/мес\n"
        text += "• +30 посещений\n\n"
        text += "📅 12 МЕСЯЦЕВ\n"
        text += "• 516.000 ₸\n"
        text += "• 48.000 ₸/мес в рассрочку\n"
        text += "• +30 посещений"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 3 месяца - 195.000 ₸", callback_data="buy_tariff_3")],
            [InlineKeyboardButton(text="📅 6 месяцев - 300.000 ₸", callback_data="buy_tariff_6")],
            [InlineKeyboardButton(text="📅 12 месяцев - 516.000 ₸", callback_data="buy_tariff_12")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=f"course_detail_{course_id}")]
        ])
        
        await callback.message.answer(text, reply_markup=keyboard)
        await callback.answer()
    except (ValueError, Exception) as e:
        logger.error(f"Ошибка при покупке абонемента: {e}", exc_info=True)
        await callback.answer("Ошибка при покупке абонемента", show_alert=True)


@router.callback_query(F.data.startswith("tariff_"))
async def tariff_selected(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора тарифа"""
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("Ошибка: неверный формат данных", show_alert=True)
            return
        
        course_id = int(parts[1])
        tariff = parts[2]
        
        # Валидация тарифа
        if tariff not in ["4", "8", "unlimited"]:
            await callback.answer("Ошибка: неверный тариф", show_alert=True)
            return
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка парсинга данных тарифа: {e}")
        await callback.answer("Ошибка: неверный формат данных", show_alert=True)
        return
    
    course = await db.get_course(course_id)
    if not course:
        await callback.answer("Курс не найден", show_alert=True)
        return
    
    # Проверяем, что центр одобрен
    if course.get("status") != "approved":
        await callback.answer("Этот курс временно недоступен", show_alert=True)
        return
    
    # Определяем цену
    price_map = {
        "4": course.get("price_4", 0),
        "8": course.get("price_8", 0),
        "unlimited": course.get("price_unlimited", 0)
    }
    price = price_map.get(tariff, 0)
    
    # Валидация цены
    if price <= 0:
        await callback.answer("Ошибка: неверная цена. Обратитесь в поддержку.", show_alert=True)
        logger.warning(f"Неверная цена для курса {course_id}, тариф {tariff}: {price}")
        return
    
    if price > 10000000:  # Защита от слишком больших сумм
        await callback.answer("Ошибка: цена слишком большая", show_alert=True)
        return
    
    # Сохраняем данные покупки
    user_id = callback.from_user.id
    await state.update_data(
        course_id=course_id,
        tariff=tariff,
        price=price
    )
    
    # Создаём временный абонемент для платежа
    import uuid
    temp_qr_id = str(uuid.uuid4())
    subscription_id = await db.create_subscription(user_id, course_id, tariff, temp_qr_id)
    
    if not subscription_id:
        await callback.answer("Ошибка при создании абонемента", show_alert=True)
        return
    
    # Инициализируем платежный сервис
    try:
        from services.payment import AirbaPayClient, PaymentService
        from config import (
            AIRBA_PAY_BASE_URL, AIRBA_PAY_USER, AIRBA_PAY_PASSWORD,
            AIRBA_PAY_TERMINAL_ID, AIRBA_PAY_COMPANY_ID, AIRBA_PAY_WEBHOOK_URL
        )
        
        # Проверяем наличие настроек
        if not AIRBA_PAY_USER or not AIRBA_PAY_PASSWORD or not AIRBA_PAY_TERMINAL_ID:
            # Если платежная система не настроена, создаём абонемент без оплаты
            qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as db_conn:
                await db_conn.execute(
                    "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                    (qr_id, subscription_id)
                )
                await db_conn.commit()
            
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
            return
        
        # Создаём платеж
        client = AirbaPayClient(
            base_url=AIRBA_PAY_BASE_URL,
            user=AIRBA_PAY_USER,
            password=AIRBA_PAY_PASSWORD,
            terminal_id=AIRBA_PAY_TERMINAL_ID,
            company_id=AIRBA_PAY_COMPANY_ID
        )
        
        payment_service = PaymentService(client, db, AIRBA_PAY_WEBHOOK_URL)
        
        # Получаем данные пользователя
        user = await db.get_user(user_id)
        phone = user.get("phone", "") if user else ""
        email = ""  # У пользователя может не быть email
        
        payment_result = await payment_service.create_payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=float(price),
            currency="KZT",
            description=f"Оплата абонемента: {course.get('name', 'Курс')}",
            language="ru",
            phone=phone,
            email=email
        )
        
        if not payment_result.get("success"):
            error_msg = payment_result.get("error", "Ошибка при создании платежа")
            await callback.message.answer(
                f"❌ Ошибка при создании платежа:\n{error_msg}\n\n"
                "Попробуйте позже или обратитесь в поддержку."
            )
            await callback.answer()
            return
        
        # Сохраняем payment_id в state для отслеживания
        await state.update_data(
            subscription_id=subscription_id,
            payment_id=payment_result.get("payment_id")
        )
        
        redirect_url = payment_result.get("redirect_url")
        
        if redirect_url:
            from utils.keyboards import get_payment_keyboard
            await callback.message.answer(
                f"💳 Оплата абонемента\n\n"
                f"Курс: {course.get('name', 'Курс')}\n"
                f"Тариф: {tariff} занятий\n"
                f"Сумма: {price} ₸\n\n"
                f"Перейдите по ссылке для оплаты:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💳 Оплатить", url=redirect_url)],
                    [InlineKeyboardButton(text="✅ Проверить платеж", callback_data=f"check_payment_{payment_result.get('payment_id')}")],
                    [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_payment_{subscription_id}")]
                ])
            )
        else:
            await callback.message.answer(
                "⚠️ Ссылка на оплату не получена. Обратитесь в поддержку."
            )
        
    except ImportError:
        # Если платежный сервис не настроен, создаём абонемент без оплаты
        qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            await db_conn.execute(
                "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                (qr_id, subscription_id)
            )
            await db_conn.commit()
        
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
        await state.clear()
    
    await callback.answer()


@router.message(F.text == "🎫 Мои абонементы")
async def my_subscriptions(message: Message):
    """Показ абонементов пользователя"""
    user_id = message.from_user.id
    subscriptions = await db.get_user_subscriptions(user_id)
    
    if not subscriptions:
        # Показываем тарифы, если нет абонементов
        text = "🎫 У тебя пока нет абонементов.\n\n"
        text += "💎 Наши тарифы:\n\n"
        text += "📅 3 МЕСЯЦА\n"
        text += "• 195.000 ₸\n"
        text += "• 70.000 ₸/мес\n"
        text += "• +30 посещений\n\n"
        text += "📅 6 МЕСЯЦЕВ\n"
        text += "• 300.000 ₸\n"
        text += "• 55.000 ₸/мес\n"
        text += "• +30 посещений\n\n"
        text += "📅 12 МЕСЯЦЕВ\n"
        text += "• 516.000 ₸\n"
        text += "• 48.000 ₸/мес в рассрочку\n"
        text += "• +30 посещений"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 3 месяца - 195.000 ₸", callback_data="buy_tariff_3")],
            [InlineKeyboardButton(text="📅 6 месяцев - 300.000 ₸", callback_data="buy_tariff_6")],
            [InlineKeyboardButton(text="📅 12 месяцев - 516.000 ₸", callback_data="buy_tariff_12")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
        return
    
    for sub in subscriptions:
        remaining = sub.get("lessons_remaining", 0)
        template_name = sub.get("template_name", "Универсальный абонемент")
        tariff = sub.get("tariff", "")
        
        if tariff == "unlimited":
            text = f"🔹 {template_name} — Безлимит"
        else:
            text = f"🔹 {template_name} — осталось {remaining} занятий"
        await message.answer(text, reply_markup=get_subscription_keyboard(sub["subscription_id"]))


@router.callback_query(F.data.startswith("show_qr_"))
async def show_qr(callback: CallbackQuery):
    """Показ QR-кода"""
    subscription_id = int(callback.data.replace("show_qr_", ""))
    
    # Получаем данные абонемента
    subscriptions = await db.get_user_subscriptions(callback.from_user.id)
    subscription = next((s for s in subscriptions if s["subscription_id"] == subscription_id), None)
    
    if not subscription:
        await callback.answer("Абонемент не найден", show_alert=True)
        return
    
    # Генерируем QR из сохранённого кода
    from utils.qr_generator import generate_qr_code
    qr_image = generate_qr_code(subscription["qr_code"])
    
    qr_bytes = qr_image.getvalue()
    await callback.message.answer_photo(
        photo=BufferedInputFile(qr_bytes, filename="qr_code.png"),
        caption="Твой QR-код для посещений"
    )
    await callback.answer()


@router.message(F.text == "🕒 Расписание")
async def schedule(message: Message):
    """Расписание занятий пользователя"""
    logger.info(f"schedule вызван для пользователя {message.from_user.id}")
    try:
        user_id = message.from_user.id
        subscriptions = await db.get_user_subscriptions(user_id)
        
        if not subscriptions:
            await message.answer(
                "🕒 У тебя пока нет активных абонементов.\n\n"
                "Купи абонемент, чтобы увидеть расписание занятий! 📚"
            )
            return
        
        # Получаем все занятия из всех центров (универсальные абонементы)
        import aiosqlite
        from datetime import datetime, timedelta
        
        text = "🕒 Твоё расписание:\n\n"
        
        # Получаем занятия на ближайшие 7 дней
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("""
                SELECT l.*, c.name as center_name, t.name as teacher_name
                FROM lessons l
                LEFT JOIN centers c ON l.center_id = c.center_id
                LEFT JOIN teachers t ON l.teacher_id = t.teacher_id
                WHERE l.date >= date(?) AND l.date <= date(?)
                AND c.status = 'approved'
                ORDER BY l.date, l.time
                LIMIT 20
            """, (today.isoformat(), week_later.isoformat())) as cursor:
                lessons = await cursor.fetchall()
        
        if not lessons:
            text += "📅 На ближайшие 7 дней занятий не запланировано.\n\n"
            text += "Партнеры еще не добавили занятия. Проверьте позже!"
        else:
            current_date = None
            for lesson in lessons:
                lesson_dict = dict(lesson)
                lesson_date = datetime.strptime(lesson_dict["date"], "%Y-%m-%d").date()
                
                # Группируем по датам
                if current_date != lesson_date:
                    if current_date is not None:
                        text += "\n"
                    text += f"📅 {lesson_date.strftime('%d.%m.%Y')}\n"
                    current_date = lesson_date
                
                lesson_time = lesson_dict.get("time", "")
                lesson_name = lesson_dict.get("name", "Занятие")
                center_name = lesson_dict.get("center_name", "Центр")
                teacher_name = lesson_dict.get("teacher_name", "")
                
                text += f"  🕒 {lesson_time} - {lesson_name}\n"
                text += f"     🏫 {center_name}\n"
                if teacher_name:
                    text += f"     👩‍🏫 {teacher_name}\n"
                text += "\n"
        
        await message.answer(text)
        logger.info(f"schedule: ответ отправлен пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка в schedule: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении расписания.")


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message):
    """Показ статистики пользователя"""
    user_id = message.from_user.id
    stats = await db.get_visit_stats(user_id)
    
    visits = stats.get("visits_count", 0)
    total = stats.get("total_lessons", 0)
    remaining = stats.get("remaining_lessons", 0)
    missed = total - visits - remaining if total > 0 else 0
    regularity = int((visits / total * 100)) if total > 0 else 0
    
    # Получаем активные абонементы
    subscriptions = await db.get_user_subscriptions(user_id)
    active_count = len([s for s in subscriptions if s.get("status") == "active"])
    
    text = "📊 Твоя статистика:\n\n"
    text += f"✅ Активных абонементов: {active_count}\n\n"
    text += f"📈 Посещений: {visits} из {total}\n"
    text += f"⏰ Пропусков: {missed}\n"
    text += f"📚 Осталось занятий: {remaining}\n\n"
    
    if total > 0:
        # Визуализация прогресса
        progress_bar_length = 10
        filled = int((visits / total) * progress_bar_length)
        progress_bar = "█" * filled + "░" * (progress_bar_length - filled)
        text += f"📊 Регулярность: {regularity}%\n"
        text += f"{progress_bar}\n"
    else:
        text += "📝 У тебя пока нет посещений.\n"
        text += "Купи абонемент и начни обучение! 🎓"
    
    await message.answer(text)


@router.message(F.text == "🆘 Поддержка")
async def support(message: Message):
    """Поддержка"""
    await message.answer(
        "🆘 Поддержка\n\n"
        "Если у тебя есть вопросы, напиши нам:\n"
        "📧 support@example.com\n"
        "📱 +7 (XXX) XXX-XX-XX"
    )


@router.callback_query(F.data.startswith("cancel_payment_"))
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Отмена платежа"""
    try:
        subscription_id = int(callback.data.replace("cancel_payment_", ""))
        user_id = callback.from_user.id
        
        # Проверяем, что абонемент принадлежит пользователю
        subscription = await db.get_user_subscriptions(user_id)
        if not any(s.get("subscription_id") == subscription_id for s in subscription):
            # Проверяем через прямой запрос
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as db_conn:
                db_conn.row_factory = aiosqlite.Row
                async with db_conn.execute(
                    "SELECT * FROM subscriptions WHERE subscription_id = ? AND user_id = ?",
                    (subscription_id, user_id)
                ) as cursor:
                    sub = await cursor.fetchone()
                    if not sub:
                        await callback.answer("Абонемент не найден или доступ запрещен", show_alert=True)
                        return
        
        # Удаляем связанные платежи
        payments = await db.get_user_payments(user_id)
        for payment in payments:
            if payment.get("subscription_id") == subscription_id:
                # Помечаем платеж как отмененный
                await db.update_payment_status(
                    payment.get("payment_id"),
                    "cancelled",
                    error_message="Отменен пользователем"
                )
        
        # Удаляем временный абонемент
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            await db_conn.execute("DELETE FROM subscriptions WHERE subscription_id = ?", (subscription_id,))
            await db_conn.commit()
        
        await callback.message.answer("❌ Платеж отменен. Абонемент не создан.")
        await callback.answer("Платеж отменен")
        await state.clear()
    except ValueError:
        await callback.answer("Ошибка: неверный ID абонемента", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при отмене платежа: {e}", exc_info=True)
        await callback.answer("Произошла ошибка при отмене платежа", show_alert=True)


@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment_status(callback: CallbackQuery, state: FSMContext):
    """Проверка статуса платежа"""
    payment_id = int(callback.data.replace("check_payment_", ""))
    user_id = callback.from_user.id
    
    try:
        from services.payment import AirbaPayClient, PaymentService
        from config import (
            AIRBA_PAY_BASE_URL, AIRBA_PAY_USER, AIRBA_PAY_PASSWORD,
            AIRBA_PAY_TERMINAL_ID, AIRBA_PAY_COMPANY_ID, AIRBA_PAY_WEBHOOK_URL
        )
        
        client = AirbaPayClient(
            base_url=AIRBA_PAY_BASE_URL,
            user=AIRBA_PAY_USER,
            password=AIRBA_PAY_PASSWORD,
            terminal_id=AIRBA_PAY_TERMINAL_ID,
            company_id=AIRBA_PAY_COMPANY_ID
        )
        
        payment_service = PaymentService(client, db, AIRBA_PAY_WEBHOOK_URL)
        result = await payment_service.get_payment_status(payment_id, user_id)
        
        if result.get("success"):
            status = result.get("status", "pending")
            payment = result.get("payment", {})
            subscription_id = payment.get("subscription_id")
            
            if status == "success":
                # Платеж успешен, активируем абонемент
                if subscription_id:
                    # Генерируем QR-код
                    qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
                    
                    # Обновляем QR-код в базе данных
                    import aiosqlite
                    async with aiosqlite.connect(db.db_path) as db_conn:
                        await db_conn.execute(
                            "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                            (qr_id, subscription_id)
                        )
                        await db_conn.commit()
                    
                    await callback.message.answer(
                        "✅ Платеж успешно выполнен!\n\n"
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
                else:
                    await callback.message.answer("✅ Платеж успешно выполнен!")
                
                await state.clear()
            elif status == "failed":
                await callback.message.answer(
                    "❌ Платеж не прошел.\n\n"
                    "Попробуйте оплатить снова или обратитесь в поддержку."
                )
            else:
                await callback.message.answer(
                    f"⏳ Статус платежа: {status}\n\n"
                    "Ожидаем подтверждения платежа..."
                )
        else:
            await callback.message.answer(
                f"❌ Ошибка при проверке платежа:\n{result.get('error', 'Неизвестная ошибка')}"
            )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при проверке платежа: {e}", exc_info=True)
        await callback.message.answer(
            f"❌ Ошибка при проверке платежа.\n\n"
            f"Попробуйте позже или обратитесь в поддержку."
        )
        await callback.answer()


@router.message(F.text == "💳 Мои платежи")
async def my_payments(message: Message):
    """Показ истории платежей пользователя"""
    logger.info(f"my_payments вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    try:
        user_id = message.from_user.id
        payments = await db.get_user_payments(user_id)
        
        if not payments:
            await message.answer("У тебя пока нет платежей.")
            return
        
        text = "💳 История платежей:\n\n"
        for payment in payments[:10]:  # Показываем последние 10
            status_emoji = {
                "success": "✅",
                "pending": "⏳",
                "failed": "❌",
                "refunded": "↩️"
            }.get(payment.get("status", "pending"), "❓")
            
            amount = payment.get("amount", 0)
            status = payment.get("status", "pending")
            created_at = payment.get("created_at", "")
            
            text += f"{status_emoji} {amount} ₸ - {status}\n"
            if created_at:
                text += f"   📅 {created_at[:10]}\n"
            text += "\n"
        
        await message.answer(text)
        logger.info(f"my_payments: ответ отправлен пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка в my_payments: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении истории платежей.")


@router.callback_query(F.data.startswith("buy_tariff_"))
async def buy_tariff(callback: CallbackQuery, state: FSMContext):
    """Покупка тарифа"""
    try:
        tariff_months = callback.data.replace("buy_tariff_", "")
        
        # Определяем параметры тарифа
        tariff_data = {
            "3": {
                "name": "Абонемент на 3 месяца",
                "price": 195000,
                "months": 3,
                "price_per_month": 70000,
                "lessons": 30,
                "tariff": "3_months"
            },
            "6": {
                "name": "Абонемент на 6 месяцев",
                "price": 300000,
                "months": 6,
                "price_per_month": 55000,
                "lessons": 30,
                "tariff": "6_months"
            },
            "12": {
                "name": "Абонемент на 12 месяцев",
                "price": 516000,
                "months": 12,
                "price_per_month": 48000,
                "lessons": 30,
                "tariff": "12_months"
            }
        }
        
        if tariff_months not in tariff_data:
            await callback.answer("Неверный тариф", show_alert=True)
            return
        
        tariff_info = tariff_data[tariff_months]
        user_id = callback.from_user.id
        price = tariff_info["price"]
        lessons = tariff_info["lessons"]
        
        # Сохраняем данные покупки
        await state.update_data(
            tariff_months=tariff_months,
            tariff_name=tariff_info["name"],
            price=price,
            lessons=lessons,
            tariff=tariff_info["tariff"]
        )
        
        # Создаём временный абонемент для платежа
        import uuid
        temp_qr_id = str(uuid.uuid4())
        
        # Создаём шаблон абонемента, если его нет
        templates = await db.get_subscription_templates(active_only=False)
        template_id = None
        
        # Ищем существующий шаблон или создаём новый
        for t in templates:
            if t.get("name") == tariff_info["name"]:
                template_id = t.get("template_id")
                break
        
        if not template_id:
            # Создаём новый шаблон
            template_id = await db.create_subscription_template(
                name=tariff_info["name"],
                description=f"Абонемент на {tariff_months} месяцев с {lessons} посещениями",
                tariff=tariff_info["tariff"],
                lessons_total=lessons,
                price=price,
                created_by=user_id
            )
        
        # Создаём абонемент
        subscription_id = await db.create_subscription(user_id, template_id, temp_qr_id)
        
        if not subscription_id:
            await callback.answer("Ошибка при создании абонемента", show_alert=True)
            return
        
        # Инициализируем платежный сервис
        try:
            from services.payment import AirbaPayClient, PaymentService
            from config import (
                AIRBA_PAY_BASE_URL, AIRBA_PAY_USER, AIRBA_PAY_PASSWORD,
                AIRBA_PAY_TERMINAL_ID, AIRBA_PAY_COMPANY_ID, AIRBA_PAY_WEBHOOK_URL
            )
            
            # Проверяем наличие настроек
            if not AIRBA_PAY_USER or not AIRBA_PAY_PASSWORD or not AIRBA_PAY_TERMINAL_ID:
                # Если платежная система не настроена, создаём абонемент без оплаты
                qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
                import aiosqlite
                async with aiosqlite.connect(db.db_path) as db_conn:
                    await db_conn.execute(
                        "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                        (qr_id, subscription_id)
                    )
                    await db_conn.commit()
                
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
                return
            
            # Создаём платеж
            client = AirbaPayClient(
                base_url=AIRBA_PAY_BASE_URL,
                user=AIRBA_PAY_USER,
                password=AIRBA_PAY_PASSWORD,
                terminal_id=AIRBA_PAY_TERMINAL_ID,
                company_id=AIRBA_PAY_COMPANY_ID
            )
            
            payment_service = PaymentService(client, db, AIRBA_PAY_WEBHOOK_URL)
            
            # Получаем данные пользователя
            user = await db.get_user(user_id)
            phone = user.get("phone", "") if user else ""
            email = ""
            
            payment_result = await payment_service.create_payment(
                user_id=user_id,
                subscription_id=subscription_id,
                amount=float(price),
                currency="KZT",
                description=f"Оплата абонемента: {tariff_info['name']}",
                language="ru",
                phone=phone,
                email=email
            )
            
            if not payment_result.get("success"):
                error_msg = payment_result.get("error", "Ошибка при создании платежа")
                await callback.message.answer(
                    f"❌ Ошибка при создании платежа:\n{error_msg}\n\n"
                    "Попробуйте позже или обратитесь в поддержку."
                )
                await callback.answer()
                return
            
            # Сохраняем payment_id в state для отслеживания
            await state.update_data(
                subscription_id=subscription_id,
                payment_id=payment_result.get("payment_id")
            )
            
            redirect_url = payment_result.get("redirect_url")
            
            if redirect_url:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                await callback.message.answer(
                    f"💳 Оплата абонемента\n\n"
                    f"Абонемент: {tariff_info['name']}\n"
                    f"Сумма: {price:,.0f} ₸\n\n"
                    f"Перейдите по ссылке для оплаты:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💳 Оплатить", url=redirect_url)],
                        [InlineKeyboardButton(text="✅ Проверить платеж", callback_data=f"check_payment_{payment_result.get('payment_id')}")],
                        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_payment_{subscription_id}")]
                    ])
                )
            else:
                await callback.message.answer(
                    "⚠️ Ссылка на оплату не получена. Обратитесь в поддержку."
                )
            
        except ImportError:
            # Если платежный сервис не настроен, создаём абонемент без оплаты
            qr_id, qr_image = generate_subscription_qr(user_id, subscription_id)
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as db_conn:
                await db_conn.execute(
                    "UPDATE subscriptions SET qr_code = ? WHERE subscription_id = ?",
                    (qr_id, subscription_id)
                )
                await db_conn.commit()
            
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
            await state.clear()
        
        await callback.answer()
    except (ValueError, Exception) as e:
        logger.error(f"Ошибка при покупке тарифа: {e}", exc_info=True)
        await callback.answer("Ошибка при покупке тарифа", show_alert=True)

