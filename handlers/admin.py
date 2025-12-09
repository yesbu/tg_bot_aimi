from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import Database
from utils.keyboards import get_admin_menu, get_moderation_keyboard
from config import ROLE_ADMIN, STATUS_APPROVED, STATUS_REJECTED, ADMIN_IDS

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    try:
        # Проверяем по ADMIN_IDS из config
        result = user_id in ADMIN_IDS
        logger.debug(f"is_admin({user_id}): ADMIN_IDS={ADMIN_IDS}, result={result}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при проверке is_admin для {user_id}: {e}")
        return False


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Вход в админ-панель"""
    try:
        logger.info(f"Обработка /admin от пользователя {message.from_user.id}")
        user_id = message.from_user.id
        
        if not is_admin(user_id):
            logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
            await message.answer("❌ У вас нет доступа к админ-панели.")
            return
        
        # Обновляем роль пользователя
        await db.update_user_role(user_id, ROLE_ADMIN)
        
        logger.info(f"Админ-панель открыта для пользователя {user_id}")
        await message.answer(
            "🔐 Админ-панель:\n\n"
            "Выбери действие:",
            reply_markup=get_admin_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при обработке /admin: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке команды.\n\n"
            "Попробуйте ещё раз или обратитесь в поддержку."
        )


@router.message((F.text == "✅ Модерация") | (F.text == "Модерация"))
async def moderation_menu(message: Message):
    """Меню модерации"""
    logger.info(f"moderation_menu вызван для пользователя {message.from_user.id}")
    if not is_admin(message.from_user.id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {message.from_user.id}")
        return
    
    try:
        pending_centers = await db.get_pending_centers()
        
        if not pending_centers:
            await message.answer("✅ Нет новых центров на модерации.")
            return
        
        # Показываем центры с кнопками одобрения/отклонения
        for center in pending_centers[:10]:  # Показываем первые 10
            text = f"📋 Центр на модерации:\n\n"
            text += f"Название: {center['name']}\n"
            text += f"ID: {center['center_id']}\n"
            text += f"Город: {center.get('city', 'Не указан')}\n"
            text += f"Адрес: {center.get('address', 'Не указан')}\n"
            text += f"Телефон: {center.get('phone', 'Не указан')}\n"
            text += f"Категория: {center.get('category', 'Не указана')}\n"
            text += f"Описание: {center.get('description', 'Нет описания')[:100]}...\n"
            
            await message.answer(
                text,
                reply_markup=get_moderation_keyboard(center['center_id'])
            )
    except Exception as e:
        logger.error(f"Ошибка в moderation_menu: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении центров на модерации.")


@router.callback_query(F.data.startswith("approve_center_"))
async def approve_center(callback: CallbackQuery):
    """Одобрение центра"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    center_id = int(callback.data.replace("approve_center_", ""))
    await db.update_center_status(center_id, STATUS_APPROVED)
    
    await callback.message.edit_text(
        f"✅ Центр #{center_id} одобрен!"
    )
    
    # В реальном приложении здесь бы было отправка уведомления партнёру
    await callback.answer()


@router.callback_query(F.data.startswith("reject_center_"))
async def reject_center(callback: CallbackQuery):
    """Отклонение центра"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    
    center_id = int(callback.data.replace("reject_center_", ""))
    await db.update_center_status(center_id, STATUS_REJECTED)
    
    await callback.message.edit_text(
        f"❌ Центр #{center_id} отклонён!"
    )
    
    # В реальном приложении здесь бы было отправка уведомления партнёру
    await callback.answer()


@router.message((F.text == "🏢 Центры") | (F.text == "  Центры") | (F.text == "Центры"))
async def admin_centers(message: Message):
    """Управление центрами"""
    logger.info(f"admin_centers вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    logger.info(f"Пользователь {user_id} является админом, получаем центры...")
    try:
        # Получаем все центры
        centers = await db.get_centers()
        
        if not centers:
            await message.answer("🏢 Центров пока нет.")
            return
        
        # Группируем по статусу
        approved = [c for c in centers if c.get("status") == STATUS_APPROVED]
        pending = [c for c in centers if c.get("status") == "pending"]
        rejected = [c for c in centers if c.get("status") == STATUS_REJECTED]
        
        text = f"🏢 Всего центров: {len(centers)}\n\n"
        text += f"✅ Одобренных: {len(approved)}\n"
        text += f"⏳ На модерации: {len(pending)}\n"
        text += f"❌ Отклоненных: {len(rejected)}\n\n"
        
        if pending:
            text += "⏳ На модерации:\n"
            for center in pending[:10]:
                text += f"• {center['name']} ({center.get('city', 'N/A')}) — ID: {center['center_id']}\n"
            text += "\n"
        
        if approved:
            text += "✅ Одобренные (первые 10):\n"
            for center in approved[:10]:
                text += f"• {center['name']} ({center.get('city', 'N/A')})\n"
        
        logger.info(f"Отправляем ответ пользователю {message.from_user.id}")
        await message.answer(text)
        logger.info(f"Ответ отправлен пользователю {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в admin_centers: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении списка центров.")


@router.message((F.text == "👥 Пользователи") | (F.text == "  Пользователи") | (F.text == "Пользователи"))
async def admin_users(message: Message):
    """Управление пользователями"""
    logger.info(f"admin_users вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    try:
        users = await db.get_all_users()
        
        text = f"👥 Всего пользователей: {len(users)}\n\n"
        
        # Подсчёт по ролям
        roles_count = {}
        for user in users:
            role = user.get("role", "user")
            roles_count[role] = roles_count.get(role, 0) + 1
        
        for role, count in roles_count.items():
            text += f"{role}: {count}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в admin_users: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении списка пользователей.")


@router.message((F.text == "🎫 Абонементы") | (F.text == "  Абонементы") | (F.text == "Абонементы"))
async def admin_subscriptions(message: Message):
    """Управление абонементами"""
    logger.info(f"admin_subscriptions вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    try:
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("SELECT COUNT(*) as count FROM subscriptions") as cursor:
                total = await cursor.fetchone()
                total_count = total["count"] if total else 0
            
            async with db_conn.execute("SELECT COUNT(*) as count FROM subscriptions WHERE status = 'active'") as cursor:
                active = await cursor.fetchone()
                active_count = active["count"] if active else 0
            
            async with db_conn.execute("SELECT COUNT(*) as count FROM subscriptions WHERE status = 'expired'") as cursor:
                expired = await cursor.fetchone()
                expired_count = expired["count"] if expired else 0
        
        text = f"🎫 Абонементы\n\n"
        text += f"📊 Всего: {total_count}\n"
        text += f"✅ Активных: {active_count}\n"
        text += f"❌ Истекших: {expired_count}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в admin_subscriptions: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении информации об абонементах.")


@router.message((F.text == "💳 Оплаты") | (F.text == "  Оплаты") | (F.text == "Оплаты"))
async def admin_payments(message: Message):
    """Управление платежами"""
    logger.info(f"admin_payments вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    try:
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("SELECT COUNT(*) as count FROM payments") as cursor:
                total = await cursor.fetchone()
                total_count = total["count"] if total else 0
            
            async with db_conn.execute("SELECT COUNT(*) as count, SUM(amount) as total_amount FROM payments WHERE status = 'success'") as cursor:
                success = await cursor.fetchone()
                success_count = success["count"] if success else 0
                total_amount = success["total_amount"] if success and success["total_amount"] else 0
            
            async with db_conn.execute("SELECT COUNT(*) as count FROM payments WHERE status = 'pending'") as cursor:
                pending = await cursor.fetchone()
                pending_count = pending["count"] if pending else 0
        
        text = f"💳 Платежи\n\n"
        text += f"📊 Всего платежей: {total_count}\n"
        text += f"✅ Успешных: {success_count}\n"
        text += f"⏳ Ожидающих: {pending_count}\n"
        if total_amount:
            text += f"💰 Общая сумма: {total_amount:,.0f} ₸\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в admin_payments: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении информации о платежах.")


@router.message((F.text == "📝 Логи посещений") | (F.text == "  Логи посещений") | (F.text == "Логи посещений"))
async def admin_visits(message: Message):
    """Логи посещений"""
    logger.info(f"admin_visits вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    try:
        import aiosqlite
        from datetime import datetime, timedelta
        
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("SELECT COUNT(*) as count FROM visits") as cursor:
                total = await cursor.fetchone()
                total_count = total["count"] if total else 0
            
            # Посещения за сегодня
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            async with db_conn.execute("""
                SELECT COUNT(*) as count FROM visits 
                WHERE date(visited_at) = date(?)
            """, (today_str,)) as cursor:
                today_visits = await cursor.fetchone()
                today_count = today_visits["count"] if today_visits else 0
            
            # Посещения за последние 7 дней
            week_ago = (datetime.now() - timedelta(days=7)).date()
            week_ago_str = week_ago.strftime('%Y-%m-%d')
            async with db_conn.execute("""
                SELECT COUNT(*) as count FROM visits 
                WHERE date(visited_at) >= date(?)
            """, (week_ago_str,)) as cursor:
                week_visits = await cursor.fetchone()
                week_count = week_visits["count"] if week_visits else 0
        
        text = f"📝 Логи посещений\n\n"
        text += f"📊 Всего посещений: {total_count}\n"
        text += f"📅 За сегодня: {today_count}\n"
        text += f"📆 За последние 7 дней: {week_count}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в admin_visits: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении логов посещений.")


@router.message((F.text == "👶 Дети / Родители") | (F.text == "  Дети / Родители") | (F.text == "Дети / Родители"))
async def admin_children_parents(message: Message):
    """Управление детьми и родителями"""
    logger.info(f"admin_children_parents вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    try:
        # Получаем всех родителей
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as db_conn:
            db_conn.row_factory = aiosqlite.Row
            async with db_conn.execute("""
                SELECT u.*, COUNT(c.child_id) as children_count
                FROM users u
                LEFT JOIN children c ON u.user_id = c.parent_id
                WHERE u.role = 'parent'
                GROUP BY u.user_id
            """) as cursor:
                parents = await cursor.fetchall()
            
            async with db_conn.execute("SELECT COUNT(*) as count FROM children") as cursor:
                children_row = await cursor.fetchone()
                children_count = children_row["count"] if children_row else 0
        
        text = f"👶 Дети и родители\n\n"
        text += f"Всего родителей: {len(parents)}\n"
        text += f"Всего детей: {children_count}\n\n"
        
        if parents:
            text += "Родители:\n"
            for parent in parents[:10]:
                parent_dict = dict(parent)
                text += f"• {parent_dict.get('full_name', 'Неизвестно')} — {parent_dict.get('children_count', 0)} детей\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка в admin_children_parents: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при получении информации о детях и родителях.")


@router.message((F.text == "📢 Рассылки") | (F.text == "  Рассылки") | (F.text == "Рассылки"))
async def admin_broadcast(message: Message, state: FSMContext):
    """Рассылки"""
    logger.info(f"admin_broadcast вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    await message.answer(
        "📢 Рассылки\n\n"
        "Отправьте сообщение для рассылки всем пользователям:\n\n"
        "Или отправьте /cancel для отмены."
    )
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(BroadcastStates.waiting_for_message)
async def broadcast_message_received(message: Message, state: FSMContext, bot: Bot):
    """Обработка сообщения для рассылки"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    broadcast_text = message.text or message.caption or ""
    
    if not broadcast_text.strip():
        await message.answer("❌ Сообщение не может быть пустым.\n\nПопробуйте еще раз или отправьте /cancel:")
        return
    
    # Подсчитываем количество пользователей
    all_users = await db.get_all_users()
    user_count = len(all_users)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        f"📢 Подтверждение рассылки\n\n"
        f"Сообщение:\n{broadcast_text[:200]}{'...' if len(broadcast_text) > 200 else ''}\n\n"
        f"Получателей: {user_count} пользователей\n\n"
        f"Подтвердите рассылку:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_broadcast")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_broadcast")]
        ])
    )
    await state.update_data(broadcast_text=broadcast_text)
    await state.set_state(BroadcastStates.waiting_for_confirmation)


@router.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтверждение рассылки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text", "")
    
    if not broadcast_text:
        await callback.answer("❌ Сообщение не найдено", show_alert=True)
        await state.clear()
        return
    
    await callback.message.edit_text("📢 Отправка рассылки...")
    
    # Получаем всех пользователей
    all_users = await db.get_all_users()
    sent_count = 0
    failed_count = 0
    
    for user in all_users:
        user_id = user.get("user_id")
        if not user_id:
            continue
        
        try:
            await bot.send_message(user_id, f"📢 Рассылка от администратора:\n\n{broadcast_text}")
            sent_count += 1
            # Небольшая задержка, чтобы не превысить лимиты API
            import asyncio
            await asyncio.sleep(0.05)  # 50ms между сообщениями
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed_count += 1
    
    await callback.message.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📊 Отправлено: {sent_count}\n"
        f"❌ Ошибок: {failed_count}\n"
        f"📈 Всего пользователей: {len(all_users)}"
    )
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    await callback.message.edit_text("❌ Рассылка отменена.")
    await callback.answer()
    await state.clear()


# Управление универсальными абонементами
class SubscriptionTemplateStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_tariff = State()
    waiting_for_lessons = State()
    waiting_for_price = State()


@router.message((F.text == "🎫 Управление абонементами") | (F.text == "  Управление абонементами") | (F.text == "Управление абонементами"))
async def admin_subscription_templates(message: Message):
    """Управление шаблонами универсальных абонементов"""
    logger.info(f"admin_subscription_templates вызван для пользователя {message.from_user.id}, текст: '{message.text}'")
    user_id = message.from_user.id
    if not is_admin(user_id):
        logger.warning(f"Попытка доступа к админ-панели от не-админа: {user_id}")
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    templates = await db.get_subscription_templates(active_only=False)
    
    text = "🎫 Универсальные абонементы\n\n"
    if not templates:
        text += "Пока нет созданных абонементов.\n\n"
    else:
        for template in templates:
            status = "✅ Активен" if template.get("is_active") else "❌ Неактивен"
            text += f"📋 {template.get('name', 'Без названия')}\n"
            text += f"   Тариф: {template.get('tariff', 'N/A')}\n"
            text += f"   Занятий: {template.get('lessons_total', 0)}\n"
            text += f"   Цена: {template.get('price', 0):,.0f} ₸\n"
            text += f"   Статус: {status}\n\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить абонемент", callback_data="add_subscription_template")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_subscription_template")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin_menu")]
        ])
    )


@router.callback_query(F.data == "add_subscription_template")
async def add_subscription_template_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления шаблона абонемента"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.answer("📋 Создание универсального абонемента\n\nВведите название абонемента:")
    await state.set_state(SubscriptionTemplateStates.waiting_for_name)
    await callback.answer()


@router.message(SubscriptionTemplateStates.waiting_for_name)
async def subscription_template_name_received(message: Message, state: FSMContext):
    """Получение названия абонемента"""
    name = message.text.strip()
    if not name or len(name) < 3:
        await message.answer("❌ Название должно содержать минимум 3 символа. Попробуйте еще раз:")
        return
    
    await state.update_data(name=name)
    await message.answer(
        f"✅ Название: {name}\n\n"
        "Введите описание абонемента (или отправьте '-' для пропуска):"
    )
    await state.set_state(SubscriptionTemplateStates.waiting_for_description)


@router.message(SubscriptionTemplateStates.waiting_for_description)
async def subscription_template_description_received(message: Message, state: FSMContext):
    """Получение описания абонемента"""
    description = message.text.strip() if message.text.strip() != "-" else None
    await state.update_data(description=description)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    await message.answer(
        "Выберите тариф:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="4 занятия", callback_data="template_tariff_4")],
            [InlineKeyboardButton(text="8 занятий", callback_data="template_tariff_8")],
            [InlineKeyboardButton(text="Безлимит", callback_data="template_tariff_unlimited")]
        ])
    )
    await state.set_state(SubscriptionTemplateStates.waiting_for_tariff)


@router.callback_query(F.data.startswith("template_tariff_"), SubscriptionTemplateStates.waiting_for_tariff)
async def subscription_template_tariff_received(callback: CallbackQuery, state: FSMContext):
    """Получение тарифа"""
    tariff = callback.data.replace("template_tariff_", "")
    await state.update_data(tariff=tariff)
    
    if tariff == "unlimited":
        await state.update_data(lessons_total=999)
        await callback.message.answer("Введите цену абонемента (в тенге):")
        await state.set_state(SubscriptionTemplateStates.waiting_for_price)
    else:
        await callback.message.answer(f"✅ Тариф: {tariff} занятий\n\nВведите количество занятий:")
        await state.set_state(SubscriptionTemplateStates.waiting_for_lessons)
    
    await callback.answer()


@router.message(SubscriptionTemplateStates.waiting_for_lessons)
async def subscription_template_lessons_received(message: Message, state: FSMContext):
    """Получение количества занятий"""
    try:
        lessons = int(message.text.strip())
        if lessons <= 0:
            await message.answer("❌ Количество занятий должно быть больше 0. Попробуйте еще раз:")
            return
        await state.update_data(lessons_total=lessons)
        await message.answer(f"✅ Занятий: {lessons}\n\nВведите цену абонемента (в тенге):")
        await state.set_state(SubscriptionTemplateStates.waiting_for_price)
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте еще раз:")


@router.message(SubscriptionTemplateStates.waiting_for_price)
async def subscription_template_price_received(message: Message, state: FSMContext):
    """Получение цены и создание шаблона"""
    try:
        price = float(message.text.strip())
        if price <= 0:
            await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
            return
        
        data = await state.get_data()
        template_id = await db.create_subscription_template(
            name=data.get("name"),
            description=data.get("description"),
            tariff=data.get("tariff"),
            lessons_total=data.get("lessons_total", 4),
            price=price,
            created_by=message.from_user.id
        )
        
        if template_id:
            await message.answer(
                f"✅ Универсальный абонемент '{data.get('name')}' успешно создан!\n\n"
                f"Тариф: {data.get('tariff')}\n"
                f"Занятий: {data.get('lessons_total', 4)}\n"
                f"Цена: {price:,.0f} ₸"
            )
        else:
            await message.answer("❌ Ошибка при создании абонемента.")
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте еще раз:")


@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu_callback(callback: CallbackQuery):
    """Возврат в админ-меню"""
    from utils.keyboards import get_admin_menu
    await callback.message.answer("Выбери действие:", reply_markup=get_admin_menu())
    await callback.answer()




