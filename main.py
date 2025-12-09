import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import Database
from middleware.error_handler import ErrorHandlerMiddleware
from middleware.logging import LoggingMiddleware
from handlers import common, user, parent, child, partner, admin

# Настройка логирования
# Настраиваем StreamHandler с правильной кодировкой для Windows
import io

# Создаем StreamHandler с UTF-8 кодировкой
if sys.platform == 'win32':
    # Для Windows используем обертку для правильной обработки Unicode
    class UTF8StreamHandler(logging.StreamHandler):
        def __init__(self, stream=None):
            if stream is None:
                stream = sys.stdout
            super().__init__(stream)
        
        def emit(self, record):
            try:
                msg = self.format(record)
                stream = self.stream
                # Пытаемся записать с обработкой ошибок кодировки
                try:
                    stream.write(msg + self.terminator)
                except UnicodeEncodeError:
                    # Если не удается закодировать, заменяем проблемные символы
                    safe_msg = msg.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                    stream.write(safe_msg + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)
    
    stream_handler = UTF8StreamHandler(sys.stdout)
else:
    stream_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding='utf-8'),
        stream_handler
    ]
)

logger = logging.getLogger(__name__)

# Проверка токена
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не установлен! Установите его в файле .env")
    sys.exit(1)

# Инициализация бота и диспетчера
try:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
except Exception as e:
    logger.error(f"Ошибка при инициализации бота: {e}")
    logger.error("Проверьте правильность BOT_TOKEN в файле .env")
    sys.exit(1)

dp = Dispatcher()
db = Database()

# Подключаем middleware
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())
dp.message.middleware(ErrorHandlerMiddleware())
dp.callback_query.middleware(ErrorHandlerMiddleware())

# Регистрация роутеров
dp.include_router(common.router)
dp.include_router(user.router)
dp.include_router(parent.router)
dp.include_router(child.router)
dp.include_router(partner.router)
dp.include_router(admin.router)

# Собираем тексты кнопок ReplyKeyboard, чтобы игнорировать их нажатия
menu_texts = set()
try:
    from utils.keyboards import (
        get_main_menu, get_parent_menu, get_child_menu,
        get_partner_menu, get_admin_menu
    )

    def _extract_reply_texts(markup):
        texts = set()
        if not markup:
            return texts
        kb = getattr(markup, "keyboard", None)
        if kb:
            for row in kb:
                for btn in row:
                    t = getattr(btn, "text", None)
                    if t:
                        texts.add(t.strip())
        return texts

    for fn in (get_main_menu, get_parent_menu, get_child_menu, get_partner_menu, get_admin_menu):
        try:
            markup = fn()
            menu_texts.update(_extract_reply_texts(markup))
        except Exception:
            pass
except Exception:
    menu_texts = set()


# Обработчик неизвестных сообщений (должен быть последним)
# Создаём отдельный роутер для неизвестных сообщений с низким приоритетом
from aiogram import Router as UnknownRouter

unknown_router = UnknownRouter()

# Используем фильтр, который НЕ перехватывает команды
# Обработчики из других роутеров будут иметь приоритет, так как они зарегистрированы раньше
@unknown_router.message(F.text & ~F.text.startswith('/'))
async def unknown_message_handler(message: Message, state: FSMContext):
    """Обработчик неизвестных текстовых сообщений"""
    # ВАЖНО: Проверяем, есть ли активное FSM состояние
    # Если есть, то это сообщение должно обрабатываться FSM обработчиками
    current_state = await state.get_state()
    if current_state:
        # Есть активное состояние FSM - не обрабатываем здесь
        # Пусть FSM обработчики обработают это сообщение
        return
    
    text = (message.text or "").strip()
    
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    # Если пользователь - админ (проверяем и по роли в БД, и по ADMIN_IDS), не обрабатываем здесь
    from config import ADMIN_IDS
    is_admin_user = (user and user.get("role") == "admin") or (user_id in ADMIN_IDS)
    
    if is_admin_user:
        # Для админа просто игнорируем все сообщения - пусть обработчики админ-панели обработают
        # НЕ логируем здесь, чтобы не засорять логи
        return
    
    # Если текст совпадает с кнопкой ReplyKeyboard — игнорируем (это должно обрабатываться другими роутерами)
    if text and text in menu_texts:
        # Это кнопка меню, но она не обработана другими роутерами
        # Возможно, обработчик еще не зарегистрирован или произошла ошибка
        # В этом случае просто игнорируем, чтобы не показывать сообщение об ошибке
        return
    
    # Если это QR-код (начинается с SUBSCRIPTION:), не обрабатываем здесь
    # Пусть обработчик партнера обработает его
    if text and text.startswith("SUBSCRIPTION:"):
        return
    
    # Если это может быть UUID (проверяем только для партнеров)
    if user and user.get("role") == "partner":
        import re
        uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        uuid_pattern_no_dashes = r'^[0-9a-fA-F]{20,}$'
        if re.match(uuid_pattern, text, re.IGNORECASE) or re.match(uuid_pattern_no_dashes, text, re.IGNORECASE):
            # Это UUID, не обрабатываем здесь (обработчик партнера обработает)
            return

    if user:
        role = user.get("role", "user")
        if role == "parent":
            from utils.keyboards import get_parent_menu
            await message.answer(
                "Используй кнопки меню для навигации.\n\n"
                "Или отправь /start для начала работы.",
                reply_markup=get_parent_menu()
            )
        elif role == "child":
            from utils.keyboards import get_child_menu
            await message.answer(
                "Используй кнопки меню для навигации.\n\n"
                "Или отправь /start для начала работы.",
                reply_markup=get_child_menu()
            )
        elif role == "partner":
            from utils.keyboards import get_partner_menu
            await message.answer(
                "Используй кнопки меню для навигации.\n\n"
                "Или отправь /start для начала работы.",
                reply_markup=get_partner_menu()
            )
        elif role == "admin":
            from utils.keyboards import get_admin_menu
            await message.answer(
                "Используй кнопки меню для навигации.\n\n"
                "Или отправь /start для начала работы.",
                reply_markup=get_admin_menu()
            )
        else:
            from utils.keyboards import get_main_menu
            await message.answer(
                "Используй кнопки меню для навигации.\n\n"
                "Или отправь /start для начала работы.",
                reply_markup=get_main_menu()
            )
    else:
        await message.answer(
            "👋 Привет! Отправь /start для начала работы."
        )

# Регистрируем роутер неизвестных сообщений ПОСЛЕ всех остальных роутеров
# В aiogram 3.x роутеры обрабатываются в порядке регистрации, поэтому этот будет последним
dp.include_router(unknown_router)

# Обработчик для всех необработанных обновлений
@dp.update()
async def unhandled_update_handler(update: Update, bot: Bot):
    """Обработчик для необработанных обновлений"""
    # Игнорируем типы, которые мы намеренно не обрабатываем
    ignored_types = ['edited_message', 'channel_post', 'edited_channel_post', 'my_chat_member', 'chat_member']
    
    # Определяем тип обновления
    if hasattr(update, 'message') and update.message:
        update_type = 'message'
        message = update.message
        
        # Обрабатываем медиа-файлы
        if message.photo:
            logger.info(f"Получено фото от {message.from_user.id}, но обработчик не найден")
            await message.answer("📷 Фото получено, но эта функция пока не поддерживается.")
            return
        
        if message.document:
            logger.info(f"Получен документ от {message.from_user.id}, но обработчик не найден")
            await message.answer("📄 Документ получен, но эта функция пока не поддерживается.")
            return
        
        if message.video:
            logger.info(f"Получено видео от {message.from_user.id}, но обработчик не найден")
            await message.answer("🎥 Видео получено, но эта функция пока не поддерживается.")
            return
        
        if message.voice:
            logger.info(f"Получено голосовое сообщение от {message.from_user.id}, но обработчик не найден")
            await message.answer("🎤 Голосовое сообщение получено, но эта функция пока не поддерживается.")
            return
        
        if message.sticker:
            # Стикеры просто игнорируем
            return
        
        if message.contact:
            logger.info(f"Получен контакт от {message.from_user.id}")
            await message.answer("📱 Контакт получен. Используйте кнопки меню для навигации.")
            return
        
        if message.location:
            logger.info(f"Получена геолокация от {message.from_user.id}")
            await message.answer("📍 Геолокация получена. Используйте кнопки меню для навигации.")
            return
        
        # Если это текстовое сообщение, но не обработано - это странно
        if message.text:
            logger.warning(f"Текстовое сообщение '{message.text[:50]}' от {message.from_user.id} не обработано")
    
    elif hasattr(update, 'callback_query') and update.callback_query:
        callback = update.callback_query
        logger.warning(f"Callback '{callback.data}' от {callback.from_user.id} не обработан")
        try:
            await callback.answer("⚠️ Эта функция временно недоступна", show_alert=False)
        except:
            pass
        return
    
    elif hasattr(update, 'poll') and update.poll:
        # Опросы игнорируем
        return
    
    elif hasattr(update, 'poll_answer') and update.poll_answer:
        # Ответы на опросы игнорируем
        return
    
    # Логируем другие типы обновлений
    update_type = getattr(update, 'event_type', type(update).__name__)
    if update_type not in ignored_types:
        logger.info(f"Необработанное обновление типа: {update_type}, ID: {update.update_id}")


async def main():
    """Запуск бота"""
    payment_checker = None
    
    try:
        # Инициализация базы данных
        await db.init_db()
        logger.info("База данных инициализирована")
        
        # Запуск автоматической проверки платежей (если настроена оплата)
        try:
            from config import AIRBA_PAY_USER, AIRBA_PAY_PASSWORD, AIRBA_PAY_TERMINAL_ID
            from services.payment import AirbaPayClient, PaymentService
            
            if AIRBA_PAY_USER and AIRBA_PAY_PASSWORD and AIRBA_PAY_TERMINAL_ID:
                from utils.payment_checker import PaymentChecker
                from config import (
                    AIRBA_PAY_BASE_URL, AIRBA_PAY_COMPANY_ID, AIRBA_PAY_WEBHOOK_URL
                )
                
                client = AirbaPayClient(
                    base_url=AIRBA_PAY_BASE_URL,
                    user=AIRBA_PAY_USER,
                    password=AIRBA_PAY_PASSWORD,
                    terminal_id=AIRBA_PAY_TERMINAL_ID,
                    company_id=AIRBA_PAY_COMPANY_ID
                )
                
                payment_service = PaymentService(client, db, AIRBA_PAY_WEBHOOK_URL)
                payment_checker = PaymentChecker(db, payment_service, check_interval=120)
                await payment_checker.start()
                logger.info("Автоматическая проверка платежей включена")
        except Exception as e:
            logger.warning(f"Не удалось запустить проверку платежей: {e}")
        
        # Определяем типы обновлений, которые нужно получать
        # Это оптимизирует работу бота и уменьшает количество необработанных обновлений
        used_update_types = dp.resolve_used_update_types()
        logger.info(f"Обрабатываемые типы обновлений: {used_update_types}")
        
        # Запуск бота
        logger.info("Бот запущен")
        await dp.start_polling(bot, allowed_updates=used_update_types)
    except KeyboardInterrupt:
        logger.info("Операция отменена")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы бота...")
        
        # Останавливаем проверку платежей
        if payment_checker:
            try:
                await payment_checker.stop()
            except Exception as e:
                logger.error(f"Ошибка при остановке проверки платежей: {e}")
        
        # Очищаем кэш
        try:
            from utils.cache import cache
            await cache.clear()
        except Exception:
            pass
        
        try:
            await bot.session.close()
            logger.info("Сессия бота закрыта")
        except Exception as e:
            logger.error(f"Ошибка при закрытии сессии: {e}")
        
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")