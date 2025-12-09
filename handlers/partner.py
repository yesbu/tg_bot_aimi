from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from utils.keyboards import get_partner_menu
from utils.validators import validate_name, validate_phone, validate_price, validate_text_length
from config import ROLE_PARTNER, STATUS_PENDING, STATUS_APPROVED, CITIES, CATEGORIES
import logging

logger = logging.getLogger(__name__)

router = Router()
db = Database()


class PartnerRegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_city = State()
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_category = State()
    waiting_for_description = State()
    waiting_for_logo = State()
    waiting_for_schedule = State()
    waiting_for_prices = State()


class TeacherStates(StatesGroup):
    waiting_for_teacher_name = State()
    waiting_for_teacher_description = State()


@router.message(Command("partner"))
async def cmd_partner(message: Message, state: FSMContext):
    """Вход для партнёра"""
    # Очищаем предыдущее состояние
    await state.clear()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await db.create_user(user_id, message.from_user.username, message.from_user.full_name, ROLE_PARTNER)
        user = await db.get_user(user_id)
    elif user.get("role") != ROLE_PARTNER:
        await db.update_user_role(user_id, ROLE_PARTNER)
    
    # Проверяем, есть ли уже центр
    center = await db.get_partner_center(user_id)
    
    if center:
        if center.get("status") == STATUS_APPROVED:
            await message.answer(
                "🏢 Добро пожаловать в панель центра!\n\n"
                f"Ваш центр: {center.get('name', 'Не указано')}\n"
                f"Статус: ✅ Одобрен\n\n"
                "Выбери действие:",
                reply_markup=get_partner_menu()
            )
        elif center.get("status") == STATUS_PENDING:
            await message.answer(
                "⏳ Ваш центр отправлен на модерацию.\n\n"
                f"Центр: {center.get('name', 'Не указано')}\n"
                "Ожидайте подтверждения от администратора.\n"
                "Вы получите уведомление после модерации.",
                reply_markup=get_partner_menu()
            )
        else:
            await message.answer(
                "❌ Ваш центр был отклонён.\n\n"
                f"Центр: {center.get('name', 'Не указано')}\n"
                "Обратитесь в поддержку для уточнения причин.\n\n"
                "Вы можете добавить новый центр через меню.",
                reply_markup=get_partner_menu()
            )
    else:
        await message.answer(
            "🏢 Добро пожаловать в панель партнёра!\n\n"
            "У вас пока нет зарегистрированного центра.\n"
            "Используйте кнопку '➕ Добавить центр' для регистрации.",
            reply_markup=get_partner_menu()
        )


@router.message(PartnerRegistrationStates.waiting_for_name)
async def partner_name_received(message: Message, state: FSMContext):
    """Название центра получено"""
    name = message.text.strip()
    
    # Валидация названия
    is_valid, error = validate_name(name)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    # Проверяем, что партнер еще не имеет центра (только если статус approved или pending)
    user_id = message.from_user.id
    existing_center = await db.get_partner_center(user_id)
    if existing_center:
        status = existing_center.get("status")
        if status == STATUS_APPROVED or status == STATUS_PENDING:
            await message.answer(
                "⚠️ У вас уже есть зарегистрированный центр.\n\n"
                f"Центр: {existing_center.get('name', 'Не указано')}\n"
                f"Статус: {'✅ Одобрен' if status == STATUS_APPROVED else '⏳ На модерации'}\n\n"
                "Один партнер может иметь только один активный центр.\n"
                "Если вы хотите изменить данные, обратитесь в поддержку."
            )
            await state.clear()
            return
        # Если центр отклонен, продолжаем регистрацию
    
    await state.update_data(name=name)
    await message.answer("Город?")
    await state.set_state(PartnerRegistrationStates.waiting_for_city)


@router.message(PartnerRegistrationStates.waiting_for_city)
async def partner_city_received(message: Message, state: FSMContext):
    """Город получен"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    city = message.text.strip() if message.text else ""
    
    if not city:
        await message.answer("❌ Город не может быть пустым.\n\nПопробуйте еще раз:")
        return
    
    # Валидация города
    is_valid, error = validate_text_length(city, min_len=2, max_len=50)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(city=city)
    await message.answer("📍 Адрес?")
    await state.set_state(PartnerRegistrationStates.waiting_for_address)


@router.message(PartnerRegistrationStates.waiting_for_address)
async def partner_address_received(message: Message, state: FSMContext):
    """Адрес получен"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    address = message.text.strip() if message.text else ""
    
    if not address:
        await message.answer("❌ Адрес не может быть пустым.\n\nПопробуйте еще раз:")
        return
    
    # Валидация адреса
    is_valid, error = validate_text_length(address, min_len=5, max_len=200)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(address=address)
    await message.answer("📞 Телефон?")
    await state.set_state(PartnerRegistrationStates.waiting_for_phone)


@router.message(PartnerRegistrationStates.waiting_for_phone)
async def partner_phone_received(message: Message, state: FSMContext):
    """Телефон получен"""
    phone = message.text.strip()
    
    # Валидация телефона
    is_valid, error = validate_phone(phone)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(phone=phone)
    await message.answer("Категория? (языки / IT / музыка / математика / ЕНТ...)")
    await state.set_state(PartnerRegistrationStates.waiting_for_category)


@router.message(PartnerRegistrationStates.waiting_for_category)
async def partner_category_received(message: Message, state: FSMContext):
    """Категория получена"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    category = message.text.strip() if message.text else ""
    
    if not category:
        await message.answer("❌ Категория не может быть пустой.\n\nПопробуйте еще раз:")
        return
    
    # Валидация категории
    is_valid, error = validate_text_length(category, min_len=2, max_len=50)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(category=category)
    await message.answer("📝 Описание центра?")
    await state.set_state(PartnerRegistrationStates.waiting_for_description)


@router.message(PartnerRegistrationStates.waiting_for_description)
async def partner_description_received(message: Message, state: FSMContext):
    """Описание получено"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    description = message.text.strip() if message.text else ""
    
    if not description:
        await message.answer("❌ Описание не может быть пустым.\n\nПопробуйте еще раз:")
        return
    
    # Валидация описания
    is_valid, error = validate_text_length(description, min_len=10, max_len=1000)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(description=description)
    await message.answer("🖼 Отправьте логотип (фото) или напишите 'пропустить':")
    await state.set_state(PartnerRegistrationStates.waiting_for_logo)


@router.message(PartnerRegistrationStates.waiting_for_logo)
async def partner_logo_received(message: Message, state: FSMContext):
    """Логотип получен"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    logo = None
    if message.photo:
        logo = message.photo[-1].file_id
    elif message.text and message.text.lower() in ["пропустить", "пропустить", "skip"]:
        pass
    else:
        await message.answer("❌ Отправьте фото или напишите 'пропустить'")
        return
    
    await state.update_data(logo=logo)
    await message.answer("🕒 Расписание? (например: Пн-Пт 10:00-18:00)")
    await state.set_state(PartnerRegistrationStates.waiting_for_schedule)


@router.message(PartnerRegistrationStates.waiting_for_schedule)
async def partner_schedule_received(message: Message, state: FSMContext):
    """Расписание получено"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    schedule = message.text.strip() if message.text else ""
    
    if not schedule:
        await message.answer("❌ Расписание не может быть пустым.\n\nПопробуйте еще раз:")
        return
    
    # Валидация расписания
    is_valid, error = validate_text_length(schedule, min_len=5, max_len=200)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(schedule=schedule)
    await message.answer(
        "💰 Укажите цены (в тенге, через запятую):\n"
        "4 занятия, 8 занятий, безлимит\n"
        "Например: 15000, 28000, 40000"
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_prices)


@router.message(PartnerRegistrationStates.waiting_for_prices)
async def partner_prices_received(message: Message, state: FSMContext):
    """Цены получены, завершение регистрации"""
    # Проверка на команду отмены
    if message.text and message.text.strip() == "/cancel":
        await state.clear()
        await message.answer("❌ Регистрация отменена.")
        return
    
    try:
        # Парсим цены
        price_strings = [p.strip() for p in message.text.split(",")]
        if len(price_strings) != 3:
            raise ValueError("Неверное количество цен")
        
        # Валидируем каждую цену
        validated_prices = []
        for i, price_str in enumerate(price_strings):
            is_valid, price, error = validate_price(price_str)
            if not is_valid:
                await message.answer(
                    f"❌ Ошибка в цене #{i+1}: {error}\n\n"
                    "Введите три числа через запятую:\n"
                    "15000, 28000, 40000"
                )
                return
            validated_prices.append(price)
        
        # Проверяем логику цен (безлимит должен быть дороже)
        if validated_prices[2] < validated_prices[1] or validated_prices[1] < validated_prices[0]:
            await message.answer(
                "⚠️ Цены должны быть в порядке возрастания:\n"
                "4 занятия < 8 занятий < безлимит\n\n"
                "Попробуйте еще раз:"
            )
            return
        
        user_id = message.from_user.id
        data = await state.get_data()
        
        # Проверяем, что все обязательные поля заполнены
        required_fields = ["name", "city", "address", "phone", "category", "description", "schedule"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            await message.answer(
                f"❌ Ошибка: не заполнены обязательные поля: {', '.join(missing_fields)}\n\n"
                "Пожалуйста, начните регистрацию заново: /partner"
            )
            await state.clear()
            return
        
        # Проверяем, что партнер еще не имеет центра (дополнительная проверка)
        existing_center = await db.get_partner_center(user_id)
        if existing_center:
            await message.answer(
                "⚠️ У вас уже есть зарегистрированный центр.\n\n"
                "Если вы хотите создать новый центр, обратитесь в поддержку."
            )
            await state.clear()
            return
        
        # Создаём центр
        try:
            center_id = await db.create_center(user_id, {
                "name": data.get("name"),
                "city": data.get("city"),
                "address": data.get("address"),
                "phone": data.get("phone"),
                "category": data.get("category"),
                "description": data.get("description"),
                "logo": data.get("logo"),
                "status": STATUS_PENDING
            })
            
            if not center_id:
                raise Exception("Не удалось создать центр")
        except Exception as e:
            logger.error(f"Ошибка при создании центра: {e}", exc_info=True)
            await message.answer(
                "❌ Ошибка при создании центра.\n\n"
                "Попробуйте позже или обратитесь в поддержку."
            )
            await state.clear()
            return
        
        # Создаём курс с ценами
        try:
            course_id = await db.create_course(center_id, {
                "name": f"Курс {data.get('name')}",
                "description": data.get("description"),
                "category": data.get("category"),
                "schedule": data.get("schedule"),
                "price_4": validated_prices[0],
                "price_8": validated_prices[1],
                "price_unlimited": validated_prices[2]
            })
            
            if not course_id:
                raise Exception("Не удалось создать курс")
        except Exception as e:
            logger.error(f"Ошибка при создании курса: {e}", exc_info=True)
            await message.answer(
                "❌ Ошибка при создании курса.\n\n"
                "Центр создан, но курс не был добавлен. Обратитесь в поддержку."
            )
            await state.clear()
            return
        
        await message.answer(
            "✅ Ваш центр отправлен на модерацию.\n\n"
            f"📋 Центр: {data.get('name')}\n"
            f"🏙 Город: {data.get('city')}\n"
            f"📞 Телефон: {data.get('phone')}\n\n"
            "Ожидайте подтверждения от администратора.\n"
            "Вы получите уведомление после модерации."
        )
        await state.clear()
        
        logger.info(f"Центр создан: center_id={center_id}, partner_id={user_id}, name={data.get('name')}")
        
    except ValueError as e:
        error_msg = str(e)
        if "Неверное количество цен" in error_msg:
            await message.answer(
                "❌ Ошибка в формате цен. Введите три числа через запятую:\n"
                "15000, 28000, 40000"
            )
        else:
            await message.answer(
                "❌ Ошибка в формате цен. Введите три числа через запятую:\n"
                "15000, 28000, 40000"
            )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при регистрации центра: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при регистрации центра.\n\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()


@router.message(F.text == "➕ Добавить центр")
async def add_center_start(message: Message, state: FSMContext):
    """Начало процесса добавления центра"""
    user_id = message.from_user.id
    
    # Проверяем, есть ли уже центр
    existing_center = await db.get_partner_center(user_id)
    
    if existing_center:
        if existing_center.get("status") == STATUS_APPROVED:
            await message.answer(
                "⚠️ У вас уже есть одобренный центр.\n\n"
                f"Центр: {existing_center.get('name', 'Не указано')}\n\n"
                "Один партнер может иметь только один центр.\n"
                "Если вы хотите изменить данные центра, обратитесь в поддержку."
            )
            return
        elif existing_center.get("status") == STATUS_PENDING:
            await message.answer(
                "⏳ У вас уже есть центр на модерации.\n\n"
                f"Центр: {existing_center.get('name', 'Не указано')}\n\n"
                "Дождитесь решения администратора.\n"
                "Если вы хотите изменить данные, обратитесь в поддержку."
            )
            return
        else:
            # Центр отклонен - можно создать новый
            await message.answer(
                "🏢 Регистрация нового центра\n\n"
                "Ваш предыдущий центр был отклонен.\n"
                "Давайте зарегистрируем новый центр.\n\n"
                "Для отмены регистрации отправьте /cancel\n\n"
                "📝 Название центра?"
            )
            await state.set_state(PartnerRegistrationStates.waiting_for_name)
            logger.info(f"Начата регистрация нового центра для партнера {user_id}")
            return
    
    # Нет центра - начинаем регистрацию
    await state.clear()
    await message.answer(
        "🏢 Регистрация учебного центра\n\n"
        "Здравствуйте! Давайте зарегистрируем ваш центр.\n\n"
        "Для отмены регистрации отправьте /cancel\n\n"
        "📝 Название центра?"
    )
    await state.set_state(PartnerRegistrationStates.waiting_for_name)
    logger.info(f"Начата регистрация центра для партнера {user_id}")


@router.message(F.text == "📋 Ученики")
async def partner_students(message: Message):
    """Список учеников партнёра"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer("Центр не найден.")
        return
    
    students = await db.get_center_students(center["center_id"])
    
    if not students:
        await message.answer("У вас пока нет учеников.")
        return
    
    text = "📋 Список учеников:\n\n"
    for student in students:
        name = student.get("child_name") or student.get("full_name", "Неизвестно")
        remaining = student.get("remaining_lessons", 0)
        text += f"• {name} — осталось {remaining} занятий\n"
    
    await message.answer(text)


@router.message(F.text == "🧾 Сканировать QR")
async def scan_qr(message: Message, state: FSMContext):
    """Режим сканирования QR"""
    await message.answer(
        "🧾 Режим сканирования QR-кода\n\n"
        "Отправьте QR-код одним из способов:\n\n"
        "1️⃣ Полный формат:\n"
        "   SUBSCRIPTION:uuid:user_id:subscription_id\n\n"
        "2️⃣ Только UUID (QR ID):\n"
        "   uuid-код\n\n"
        "Пример: 7d011397-3b4f-468f-b8ee-9900ccb8afe0\n\n"
        "Внимание: В реальном приложении здесь был бы режим камеры Telegram."
    )


@router.message(F.text.startswith("SUBSCRIPTION:"))
async def qr_scanned_full_format(message: Message):
    """Обработка полного формата QR-кода: SUBSCRIPTION:uuid:user_id:subscription_id"""
    await qr_scanned_internal(message)


@router.message(F.text & ~F.text.startswith("SUBSCRIPTION:") & ~F.text.startswith("/"))
async def qr_scanned_uuid(message: Message, state: FSMContext):
    """Обработка UUID формата QR-кода"""
    import re
    
    # Проверяем, есть ли активное FSM состояние
    # Если есть, не обрабатываем здесь (FSM обработчики должны обработать)
    current_state = await state.get_state()
    if current_state:
        return
    
    # Сначала проверяем, что пользователь является партнером
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user or user.get("role") != ROLE_PARTNER:
        # Не партнер - не обрабатываем здесь
        return
    
    # Проверяем, что это может быть UUID или QR ID
    text = message.text.strip()
    
    # Проверяем, является ли это UUID (с дефисами или без)
    uuid_pattern_with_dashes = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    uuid_pattern_without_dashes = r'^[0-9a-fA-F]{20,}$'  # Минимум 20 символов для UUID без дефисов
    
    # Проверяем, что это не кнопка меню
    from utils.keyboards import get_partner_menu
    menu = get_partner_menu()
    menu_texts = set()
    if menu and hasattr(menu, "keyboard"):
        for row in menu.keyboard:
            for btn in row:
                if hasattr(btn, "text"):
                    menu_texts.add(btn.text.strip())
    
    if text in menu_texts:
        # Это кнопка меню, не обрабатываем здесь
        return
    
    # Проверяем, похоже ли на UUID
    is_uuid = False
    if re.match(uuid_pattern_with_dashes, text, re.IGNORECASE):
        is_uuid = True
    elif re.match(uuid_pattern_without_dashes, text, re.IGNORECASE):
        is_uuid = True
    
    if is_uuid:
        # Это UUID, обрабатываем как QR-код
        logger.info(f"Обнаружен UUID в сообщении партнера: {text[:50]}")
        await qr_scanned_internal(message)
        return  # Важно: возвращаемся, чтобы не обрабатывать дальше
    # Если не UUID, не обрабатываем (другие обработчики обработают)


async def qr_scanned_internal(message: Message):
    """Обработка отсканированного QR-кода"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем, что пользователь является партнером
        user_id = message.from_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await message.answer(
                "❌ Вы не зарегистрированы в системе.\n\n"
                "Отправьте /start для регистрации."
            )
            return
        
        # Проверяем роль партнера
        if user.get("role") != ROLE_PARTNER:
            await message.answer(
                "❌ Эта функция доступна только для партнеров.\n\n"
                "Используйте команду /partner для входа в панель партнера."
            )
            return
        
        # Проверяем наличие центра
        center = await db.get_partner_center(user_id)
        if not center:
            await message.answer(
                "❌ У вас нет зарегистрированного центра.\n\n"
                "Используйте команду /partner для регистрации центра."
            )
            return
        
        # Проверяем статус центра
        if center.get("status") != STATUS_APPROVED:
            await message.answer(
                "❌ Ваш центр не одобрен администратором.\n\n"
                f"Статус: {'⏳ На модерации' if center.get('status') == STATUS_PENDING else '❌ Отклонен'}\n"
                "Дождитесь одобрения центра для использования функции сканирования QR-кодов."
            )
            return
        
        # Парсим QR-код
        qr_text = message.text.strip()
        qr_id = None
        
        # Проверяем формат QR-кода
        if qr_text.startswith("SUBSCRIPTION:"):
            # Полный формат: SUBSCRIPTION:uuid:user_id:subscription_id
            parts = qr_text.split(":")
            if len(parts) < 4:
                await message.answer(
                    "❌ Неверный формат QR-кода.\n\n"
                    "Ожидается формат: SUBSCRIPTION:uuid:user_id:subscription_id\n\n"
                    "Убедитесь, что вы скопировали QR-код полностью."
                )
                return
            qr_id = parts[1].strip()
        else:
            # Возможно, это только UUID
            # Проверяем, похоже ли на UUID (содержит дефисы и имеет длину ~36 символов)
            import re
            uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
            if re.match(uuid_pattern, qr_text):
                # Это UUID, используем его напрямую
                qr_id = qr_text
                logger.info(f"Обнаружен UUID формат: {qr_id}")
            else:
                # Пробуем использовать как QR ID (может быть без дефисов)
                # Убираем все пробелы и проверяем длину
                cleaned = qr_text.replace(" ", "").replace("-", "")
                if len(cleaned) >= 20:  # Минимальная длина для UUID без дефисов
                    qr_id = cleaned
                    logger.info(f"Обнаружен QR ID без дефисов: {qr_id}")
                else:
                    await message.answer(
                        "❌ Неверный формат QR-кода.\n\n"
                        "Поддерживаемые форматы:\n"
                        "• SUBSCRIPTION:uuid:user_id:subscription_id\n"
                        "• UUID (например: 7d011397-3b4f-468f-b8ee-9900ccb8afe0)\n\n"
                        "Проверьте правильность QR-кода и попробуйте еще раз."
                    )
                    return
        
        # Валидация UUID/QR ID
        if not qr_id or len(qr_id) < 10:
            await message.answer(
                "❌ Неверный формат QR-кода.\n\n"
                "QR ID слишком короткий или отсутствует.\n"
                "Минимальная длина: 10 символов."
            )
            return
        
        logger.info(f"Попытка сканирования QR-кода: qr_id={qr_id}, partner_id={user_id}, center_id={center['center_id']}")
        
        # Получаем абонемент по QR-коду
        subscription = await db.get_subscription_by_qr(qr_id)
        
        if not subscription:
            await message.answer(
                "❌ Абонемент не найден или недействителен.\n\n"
                "Возможные причины:\n"
                "• QR-код неверный или устарел\n"
                "• Абонемент был удален\n"
                "• Абонемент неактивен\n\n"
                "Проверьте правильность QR-кода и попробуйте еще раз."
            )
            logger.warning(f"Абонемент не найден по QR-коду: qr_id={qr_id}")
            return
        
        # Проверяем статус абонемента
        if subscription.get("status") != "active":
            status_text = {
                "expired": "истек",
                "pending": "ожидает активации",
                "cancelled": "отменен"
            }.get(subscription.get("status"), "неактивен")
            
            await message.answer(
                f"❌ Абонемент {status_text}.\n\n"
                "Обратитесь к администратору для уточнения."
            )
            return
        
        # Универсальные абонементы работают во всех центрах - проверка принадлежности не нужна
        
        # Проверяем, не закончились ли занятия (перед записью)
        remaining_before = subscription.get("lessons_remaining", 0)
        tariff = subscription.get("tariff", "")
        
        if tariff != "unlimited" and remaining_before <= 0:
            await message.answer(
                "❌ У абонемента закончились занятия.\n\n"
                f"Осталось занятий: 0\n"
                "Попросите ученика продлить абонемент."
            )
            return
        
        # Записываем посещение
        subscription_id = subscription["subscription_id"]
        logger.info(f"Попытка записи посещения: subscription_id={subscription_id}, center_id={center['center_id']}")
        
        success = await db.record_visit(
            subscription_id,
            center["center_id"]
        )
        
        if not success:
            # Проверяем причину неудачи
            # Получаем актуальные данные абонемента для диагностики
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as db_conn:
                db_conn.row_factory = aiosqlite.Row
                async with db_conn.execute(
                    "SELECT * FROM subscriptions WHERE subscription_id = ?",
                    (subscription["subscription_id"],)
                ) as cursor:
                    current_sub = await cursor.fetchone()
                    if current_sub:
                        current_sub = dict(current_sub)
                        if current_sub.get("status") != "active":
                            await message.answer(
                                "❌ Абонемент неактивен или истек.\n\n"
                                "Обратитесь к администратору."
                            )
                        elif current_sub.get("lessons_remaining", 0) <= 0 and current_sub.get("tariff") != "unlimited":
                            await message.answer(
                                "❌ У абонемента закончились занятия.\n\n"
                                "Попросите ученика продлить абонемент."
                            )
                        else:
                            await message.answer(
                                "⚠️ Посещение не записано.\n\n"
                                "Возможно, это дубликат (посещение уже было записано в последние 5 минут).\n"
                                "Попробуйте еще раз через несколько минут."
                            )
                    else:
                        await message.answer("❌ Ошибка при записи посещения. Попробуйте еще раз.")
            logger.error(f"Ошибка при записи посещения для subscription_id={subscription['subscription_id']}")
            return
        
        # Получаем обновленные данные абонемента после записи посещения
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute(
                "SELECT lessons_remaining, status, tariff FROM subscriptions WHERE subscription_id = ?",
                (subscription_id,)
            ) as cursor:
                updated_sub = await cursor.fetchone()
                if updated_sub:
                    updated_sub = dict(updated_sub)
                    remaining = updated_sub.get("lessons_remaining", 0)
                    status_after = updated_sub.get("status", "active")
                else:
                    # Если не удалось получить данные, используем расчетное значение
                    remaining = max(0, remaining_before - 1) if tariff != "unlimited" else remaining_before
                    status_after = subscription.get("status", "active")
        
        student_name = subscription.get("child_name") or subscription.get("owner_name", "Ученик")
        template_name = subscription.get("template_name", "Универсальный абонемент")
        
        # Формируем ответ
        response_text = f"✅ Посещение подтверждено!\n\n"
        response_text += f"👤 Ученик: {student_name}\n"
        response_text += f"🎫 Абонемент: {template_name}\n"
        
        if tariff == "unlimited":
            response_text += f"📊 Тариф: Безлимит\n"
        else:
            response_text += f"📊 Осталось занятий: {remaining}\n"
            if remaining == 0:
                response_text += f"⚠️ Абонемент истек\n"
        
        await message.answer(response_text)
        
        logger.info(
            f"Посещение успешно записано: subscription_id={subscription_id}, "
            f"center_id={center['center_id']}, student={student_name}, "
            f"remaining={remaining}, status_after={status_after}"
        )
        
        # Логируем успешное посещение
        logger.info(
            f"Посещение записано: subscription_id={subscription['subscription_id']}, "
            f"center_id={center['center_id']}, student={student_name}"
        )
        
        # Отправляем уведомление родителю (если это ребёнок)
        if subscription.get("child_id"):
            parent_id = subscription.get("user_id")
            # В реальном приложении здесь бы была отправка сообщения родителю
            # await bot.send_message(parent_id, f"✅ {student_name} посетил занятие!")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке QR-кода: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке QR-кода.\n\n"
            "Попробуйте еще раз или обратитесь в поддержку."
        )


@router.message(F.text == "🗓 Расписание")
async def partner_schedule(message: Message):
    """Расписание занятий партнёра"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer("Центр не найден.")
        return
    
    # Получаем курсы центра
    import aiosqlite
    async with aiosqlite.connect(db.db_path) as db_conn:
        db_conn.row_factory = aiosqlite.Row
        async with db_conn.execute("""
            SELECT * FROM courses WHERE center_id = ?
        """, (center["center_id"],)) as cursor:
            courses = await cursor.fetchall()
    
    if not courses:
        await message.answer("У вас пока нет курсов.")
        return
    
    text = "🗓 Расписание занятий:\n\n"
    for course in courses:
        course_dict = dict(course)
        text += f"📚 {course_dict.get('name', 'Курс')}\n"
        text += f"🕒 {course_dict.get('schedule', 'Не указано')}\n\n"
    
    await message.answer(text)


@router.message(F.text == "🎓 Курсы")
async def partner_courses(message: Message):
    """Управление курсами партнёра"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer("Центр не найден.")
        return
    
    # Получаем курсы центра
    import aiosqlite
    async with aiosqlite.connect(db.db_path) as db_conn:
        db_conn.row_factory = aiosqlite.Row
        async with db_conn.execute("""
            SELECT * FROM courses WHERE center_id = ?
        """, (center["center_id"],)) as cursor:
            courses = await cursor.fetchall()
    
    if not courses:
        await message.answer(
            "🎓 У вас пока нет курсов.\n\n"
            "Используйте команду /partner для добавления курсов."
        )
        return
    
    text = f"🎓 Ваши курсы ({len(courses)}):\n\n"
    for course in courses:
        course_dict = dict(course)
        text += f"📚 {course_dict.get('name', 'Курс')}\n"
        text += f"📂 {course_dict.get('category', 'Не указана')}\n"
        text += f"💰 От {course_dict.get('price_4', 0):,} ₸\n\n"
    
    await message.answer(text)


@router.message(F.text == "👩‍🏫 Преподаватели")
async def partner_teachers(message: Message):
    """Управление преподавателями"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer("❌ Центр не найден.\n\nИспользуйте команду /partner для регистрации центра.")
        return
    
    # Получаем преподавателей центра
    teachers = await db.get_teachers(center["center_id"])
    
    if not teachers:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await message.answer(
            "👩‍🏫 Преподаватели\n\n"
            "У вас пока нет зарегистрированных преподавателей.\n\n"
            "Добавьте первого преподавателя:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Добавить преподавателя", callback_data="add_teacher")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_partner_menu")]
            ])
        )
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    text = f"👩‍🏫 Преподаватели центра ({len(teachers)}):\n\n"
    keyboard = []
    
    for teacher in teachers:
        teacher_dict = dict(teacher)
        text += f"👤 {teacher_dict.get('name', 'Преподаватель')}\n"
        if teacher_dict.get('description'):
            desc = teacher_dict.get('description', '')[:50]
            text += f"   📝 {desc}{'...' if len(teacher_dict.get('description', '')) > 50 else ''}\n"
        text += "\n"
        keyboard.append([InlineKeyboardButton(
            text=f"✏️ {teacher_dict.get('name', 'Преподаватель')}",
            callback_data=f"edit_teacher_{teacher_dict.get('teacher_id')}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="➕ Добавить преподавателя", callback_data="add_teacher")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_partner_menu")])
    
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


@router.message(F.text == "⚙ Настройки")
async def partner_settings(message: Message):
    """Настройки партнёра"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer("Центр не найден.")
        return
    
    text = "⚙ Настройки центра:\n\n"
    text += f"Название: {center.get('name', 'Не указано')}\n"
    text += f"Город: {center.get('city', 'Не указан')}\n"
    text += f"Адрес: {center.get('address', 'Не указан')}\n"
    text += f"Телефон: {center.get('phone', 'Не указан')}\n"
    text += f"Категория: {center.get('category', 'Не указана')}\n"
    text += f"Статус: {center.get('status', 'Неизвестен')}\n\n"
    text += "Для изменения настроек обратитесь в поддержку."
    
    await message.answer(text)


@router.message(F.text == "📊 Аналитика")
async def partner_analytics(message: Message):
    """Аналитика для партнёра"""
    user_id = message.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await message.answer(
            "❌ Центр не найден.\n\n"
            "Используйте команду /partner для регистрации центра."
        )
        return
    
    # Получаем аналитику
    try:
        analytics = await db.get_center_analytics(center["center_id"])
        
        # Получаем количество активных абонементов
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("""
                SELECT COUNT(*) as count FROM subscriptions 
                WHERE center_id = ? AND status = 'active'
            """, (center["center_id"],)) as cursor:
                active_subs = await cursor.fetchone()
                active_count = active_subs["count"] if active_subs else 0
            
            # Получаем количество курсов
            async with db_conn.execute("""
                SELECT COUNT(*) as count FROM courses 
                WHERE center_id = ?
            """, (center["center_id"],)) as cursor:
                courses = await cursor.fetchone()
                courses_count = courses["count"] if courses else 0
        
        text = "📊 Аналитика центра\n\n"
        text += f"🏢 Центр: {center.get('name', 'Не указано')}\n\n"
        
        text += "📈 Общая статистика:\n"
        text += f"   📚 Курсов: {courses_count}\n"
        text += f"   🎫 Активных абонементов: {active_count}\n"
        text += f"   👥 Всего посещений: {analytics.get('visits_count', 0)}\n"
        text += f"   💰 Продано абонементов: {analytics.get('sales_count', 0)}\n"
        text += f"   💵 Доход: {analytics.get('total_revenue', 0):,} ₸\n\n"
        
        # Получаем статистику по посещениям за последние 7 дней
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
        
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("""
                SELECT COUNT(*) as count FROM visits 
                WHERE center_id = ? AND date(visited_at) >= date(?)
            """, (center["center_id"], seven_days_ago_str)) as cursor:
                recent_visits = await cursor.fetchone()
                recent_count = recent_visits["count"] if recent_visits else 0
        
        text += "📅 За последние 7 дней:\n"
        text += f"   👥 Посещений: {recent_count}\n"
        
        if recent_count > 0:
            avg_per_day = recent_count / 7
            text += f"   📊 В среднем в день: {avg_per_day:.1f}\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Ошибка при получении аналитики: {e}", exc_info=True)
        await message.answer(
            "❌ Ошибка при получении аналитики.\n\n"
            "Попробуйте еще раз или обратитесь в поддержку."
        )


@router.callback_query(F.data == "add_teacher")
async def add_teacher_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления преподавателя"""
    user_id = callback.from_user.id
    center = await db.get_partner_center(user_id)
    
    if not center:
        await callback.answer("❌ Центр не найден", show_alert=True)
        return
    
    await callback.message.answer(
        "👩‍🏫 Добавление преподавателя\n\n"
        "Введите имя преподавателя:"
    )
    await state.set_state(TeacherStates.waiting_for_teacher_name)
    await state.update_data(center_id=center["center_id"])
    await callback.answer()


@router.message(TeacherStates.waiting_for_teacher_name)
async def teacher_name_received(message: Message, state: FSMContext):
    """Обработка имени преподавателя"""
    from utils.validators import validate_name
    
    name = message.text.strip()
    is_valid, error = validate_name(name)
    
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте еще раз:")
        return
    
    await state.update_data(teacher_name=name)
    await state.set_state(TeacherStates.waiting_for_teacher_description)
    await message.answer(
        f"✅ Имя: {name}\n\n"
        "Введите описание преподавателя (или отправьте '-' для пропуска):"
    )


@router.message(TeacherStates.waiting_for_teacher_description)
async def teacher_description_received(message: Message, state: FSMContext):
    """Обработка описания преподавателя"""
    data = await state.get_data()
    center_id = data.get("center_id")
    name = data.get("teacher_name")
    description = message.text.strip() if message.text.strip() != "-" else None
    
    if description and len(description) > 500:
        await message.answer("❌ Описание слишком длинное (максимум 500 символов).\n\nПопробуйте еще раз:")
        return
    
    try:
        teacher_id = await db.create_teacher(center_id, name, description)
        if teacher_id:
            await message.answer(
                f"✅ Преподаватель '{name}' успешно добавлен!\n\n"
                "Вы можете добавить еще преподавателей через меню '👩‍🏫 Преподаватели'."
            )
        else:
            await message.answer("❌ Ошибка при добавлении преподавателя.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении преподавателя: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при добавлении преподавателя.")
    
    await state.clear()


@router.callback_query(F.data.startswith("edit_teacher_"))
async def edit_teacher(callback: CallbackQuery):
    """Редактирование преподавателя"""
    try:
        teacher_id = int(callback.data.replace("edit_teacher_", ""))
        teacher = await db.get_teacher(teacher_id)
        
        if not teacher:
            await callback.answer("❌ Преподаватель не найден", show_alert=True)
            return
        
        text = f"👩‍🏫 {teacher.get('name', 'Преподаватель')}\n\n"
        if teacher.get('description'):
            text += f"📝 {teacher.get('description')}\n\n"
        text += "Функция редактирования в разработке."
        
        await callback.message.answer(text)
        await callback.answer()
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID преподавателя", show_alert=True)


@router.callback_query(F.data == "back_to_partner_menu")
async def back_to_partner_menu_callback(callback: CallbackQuery):
    """Возврат в меню партнера"""
    from utils.keyboards import get_partner_menu
    await callback.message.answer("Выбери действие:", reply_markup=get_partner_menu())
    await callback.answer()

