# Handlers из old/ - Полный список

## Обзор

| Файл | Строк | Handlers | Статус |
|------|-------|----------|--------|
| `common.py` | 139 | 2 | ✅ Переписан |
| `user.py` | 1524 | 28 | 🔄 Частично |
| `partner.py` | 1140 | 24 | 🔄 Частично |
| `admin.py` | 654 | 18 | 🔄 Частично |
| `parent.py` | 416 | 14 | 🔄 Частично |
| `child.py` | 59 | 3 | 🔄 Частично |
| **ИТОГО** | **5676** | **89** | |

---

## common.py (2 handlers)

### Commands
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `cmd_start` | `/start` | Приветствие, создание пользователя, показ меню по роли | ✅ |
| `cmd_cancel` | `/cancel` | Отмена текущей FSM операции | ✅ |

---

## user.py (28 handlers)

### FSM States
```python
class SearchStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_age = State()
```

### Message Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `catalog_menu` | `F.text == "📚 Каталог курсов"` | Показ меню поиска курсов | ⏳ |
| `my_subscriptions` | `F.text == "🎫 Мои абонементы"` | Показ абонементов или тарифов | ⏳ |
| `schedule` | `F.text == "🕒 Расписание"` | Расписание занятий | ⏳ |
| `statistics` | `F.text == "📊 Статистика"` | Статистика пользователя | ⏳ |
| `support` | `F.text == "🆘 Поддержка"` | Контакты поддержки | ✅ |
| `my_payments` | `F.text == "💳 Мои платежи"` | История платежей | ⏳ |
| `age_received` | `SearchStates.waiting_for_age` | Обработка возраста для поиска | ⏳ |

### Callback Handlers - Поиск
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `select_city` | `F.data == "search_city"` | Выбор города | ⏳ |
| `select_category` | `F.data == "search_category"` | Выбор категории | ⏳ |
| `select_price` | `F.data == "search_price"` | Поиск по цене | ⏳ |
| `select_age` | `F.data == "search_age"` | Поиск по возрасту | ⏳ |
| `select_rating` | `F.data == "search_rating"` | Поиск по рейтингу | ⏳ |
| `price_range_selected` | `F.data.startswith("price_range_")` | Выбор диапазона цены | ⏳ |
| `min_rating_selected` | `F.data.startswith("min_rating_")` | Выбор мин. рейтинга | ⏳ |
| `city_selected` | `F.data.startswith("city_")` | Обработка выбора города | ⏳ |
| `category_selected` | `F.data.startswith("category_")` | Показ курсов по категории | ⏳ |
| `back_to_search` | `F.data == "back_to_search"` | Возврат к поиску | ⏳ |
| `back_to_catalog` | `F.data == "back_to_catalog"` | Возврат к каталогу | ⏳ |

### Callback Handlers - Курсы
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `course_detail` | `F.data.startswith("course_detail_")` | Детали курса | ⏳ |
| `show_reviews` | `F.data.startswith("reviews_")` | Отзывы о курсе | ⏳ |

### Callback Handlers - Абонементы
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `buy_template` | `F.data.startswith("buy_template_")` | Покупка универсального абонемента | ⏳ |
| `buy_course` | `F.data.startswith("buy_course_")` | Покупка абонемента на курс | ⏳ |
| `buy_tariff` | `F.data.startswith("buy_tariff_")` | Покупка тарифа (3/6/12 мес) | ⏳ |
| `tariff_selected` | `F.data.startswith("tariff_")` | Обработка выбора тарифа | ⏳ |
| `show_qr` | `F.data.startswith("show_qr_")` | Показ QR-кода | ⏳ |
| `extend_subscription` | `F.data.startswith("extend_")` | Продление абонемента | ⏳ |
| `subscription_history` | `F.data.startswith("history_")` | История посещений | ⏳ |

### Callback Handlers - Платежи
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `check_payment_status` | `F.data.startswith("check_payment_")` | Проверка статуса платежа | ⏳ |
| `cancel_payment` | `F.data.startswith("cancel_payment_")` | Отмена платежа | ⏳ |

---

## partner.py (24 handlers)

### FSM States
```python
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
```

### Command Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `cmd_partner` | `/partner` | Вход в панель партнёра | ⏳ |

### Message Handlers - Меню
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `add_center_start` | `F.text == "➕ Добавить центр"` | Начало регистрации центра | ⏳ |
| `partner_students` | `F.text == "📋 Ученики"` | Список учеников | ⏳ |
| `scan_qr` | `F.text == "🧾 Сканировать QR"` | Режим сканирования | ⏳ |
| `partner_schedule` | `F.text == "🗓 Расписание"` | Расписание занятий | ⏳ |
| `partner_courses` | `F.text == "🎓 Курсы"` | Управление курсами | ⏳ |
| `partner_teachers` | `F.text == "👩‍🏫 Преподаватели"` | Управление преподавателями | ⏳ |
| `partner_settings` | `F.text == "⚙ Настройки"` | Настройки центра | ⏳ |
| `partner_analytics` | `F.text == "📊 Аналитика"` | Аналитика центра | ⏳ |

### Message Handlers - FSM Регистрация центра
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `partner_name_received` | `PartnerRegistrationStates.waiting_for_name` | Название центра | ⏳ |
| `partner_city_received` | `PartnerRegistrationStates.waiting_for_city` | Город | ⏳ |
| `partner_address_received` | `PartnerRegistrationStates.waiting_for_address` | Адрес | ⏳ |
| `partner_phone_received` | `PartnerRegistrationStates.waiting_for_phone` | Телефон | ⏳ |
| `partner_category_received` | `PartnerRegistrationStates.waiting_for_category` | Категория | ⏳ |
| `partner_description_received` | `PartnerRegistrationStates.waiting_for_description` | Описание | ⏳ |
| `partner_logo_received` | `PartnerRegistrationStates.waiting_for_logo` | Логотип | ⏳ |
| `partner_schedule_received` | `PartnerRegistrationStates.waiting_for_schedule` | Расписание | ⏳ |
| `partner_prices_received` | `PartnerRegistrationStates.waiting_for_prices` | Цены, завершение | ⏳ |

### Message Handlers - FSM Преподаватели
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `teacher_name_received` | `TeacherStates.waiting_for_teacher_name` | Имя преподавателя | ⏳ |
| `teacher_description_received` | `TeacherStates.waiting_for_teacher_description` | Описание преподавателя | ⏳ |

### Message Handlers - QR Сканирование
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `qr_scanned_full_format` | `F.text.startswith("SUBSCRIPTION:")` | Полный формат QR | ⏳ |
| `qr_scanned_uuid` | UUID pattern | UUID формат QR | ⏳ |

### Callback Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `add_teacher_start` | `F.data == "add_teacher"` | Добавление преподавателя | ⏳ |
| `edit_teacher` | `F.data.startswith("edit_teacher_")` | Редактирование преподавателя | ⏳ |
| `back_to_partner_menu_callback` | `F.data == "back_to_partner_menu"` | Возврат в меню | ⏳ |

---

## admin.py (18 handlers)

### FSM States
```python
class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()

class SubscriptionTemplateStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_tariff = State()
    waiting_for_lessons = State()
    waiting_for_price = State()
```

### Command Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `cmd_admin` | `/admin` | Вход в админ-панель | ⏳ |

### Message Handlers - Меню
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `moderation_menu` | `F.text == "✅ Модерация"` | Модерация центров | ⏳ |
| `admin_centers` | `F.text == "🏢 Центры"` | Управление центрами | ⏳ |
| `admin_users` | `F.text == "👥 Пользователи"` | Управление пользователями | ⏳ |
| `admin_subscriptions` | `F.text == "🎫 Абонементы"` | Статистика абонементов | ⏳ |
| `admin_payments` | `F.text == "💳 Оплаты"` | Статистика платежей | ⏳ |
| `admin_visits` | `F.text == "📝 Логи посещений"` | Логи посещений | ⏳ |
| `admin_children_parents` | `F.text == "👶 Дети / Родители"` | Управление детьми/родителями | ⏳ |
| `admin_broadcast` | `F.text == "📢 Рассылки"` | Начало рассылки | ⏳ |
| `admin_subscription_templates` | `F.text == "🎫 Управление абонементами"` | Шаблоны абонементов | ⏳ |

### Message Handlers - FSM Рассылка
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `broadcast_message_received` | `BroadcastStates.waiting_for_message` | Текст рассылки | ⏳ |

### Message Handlers - FSM Шаблоны абонементов
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `subscription_template_name_received` | `SubscriptionTemplateStates.waiting_for_name` | Название | ⏳ |
| `subscription_template_description_received` | `SubscriptionTemplateStates.waiting_for_description` | Описание | ⏳ |
| `subscription_template_lessons_received` | `SubscriptionTemplateStates.waiting_for_lessons` | Кол-во занятий | ⏳ |
| `subscription_template_price_received` | `SubscriptionTemplateStates.waiting_for_price` | Цена | ⏳ |

### Callback Handlers - Модерация
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `approve_center` | `F.data.startswith("approve_center_")` | Одобрить центр | ⏳ |
| `reject_center` | `F.data.startswith("reject_center_")` | Отклонить центр | ⏳ |

### Callback Handlers - Рассылка
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `confirm_broadcast` | `F.data == "confirm_broadcast"` | Подтвердить рассылку | ⏳ |
| `cancel_broadcast` | `F.data == "cancel_broadcast"` | Отменить рассылку | ⏳ |

### Callback Handlers - Шаблоны
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `add_subscription_template_start` | `F.data == "add_subscription_template"` | Добавить шаблон | ⏳ |
| `subscription_template_tariff_received` | `F.data.startswith("template_tariff_")` | Выбор тарифа | ⏳ |
| `back_to_admin_menu_callback` | `F.data == "back_to_admin_menu"` | Возврат в меню | ⏳ |

---

## parent.py (14 handlers)

### FSM States
```python
class ParentStates(StatesGroup):
    waiting_for_child_name = State()
    waiting_for_child_age = State()
    buying_for_child = State()
```

### Message Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `my_children` | `F.text == "🧒 Мои дети"` | Список детей | ⏳ |
| `buy_subscription_menu` | `F.text == "🎫 Купить абонемент"` | Покупка для ребёнка | ⏳ |
| `children_attendance` | `F.text == "📊 Посещаемость"` | Статистика посещений | ⏳ |
| `parent_schedule` | `F.text == "📅 Расписание"` | Расписание детей | ⏳ |
| `parent_purchases` | `F.text == "💳 Покупки"` | История покупок | ⏳ |

### Message Handlers - FSM
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `child_name_received` | `ParentStates.waiting_for_child_name` | Имя ребёнка | ⏳ |
| `child_age_received` | `ParentStates.waiting_for_child_age` | Возраст ребёнка | ⏳ |

### Callback Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `add_child_start` | `F.data == "parent_add_child"` | Добавить ребёнка | ⏳ |
| `parent_skip` | `F.data == "parent_skip"` | Пропустить | ⏳ |
| `child_selected_for_purchase` | `F.data.startswith("select_child_")` | Выбор ребёнка для покупки | ⏳ |
| `parent_select_city` | `F.data == "search_city"` + `ParentStates.buying_for_child` | Выбор города | ⏳ |
| `parent_city_selected` | `F.data.startswith("city_")` + state | Город выбран | ⏳ |
| `parent_category_selected` | `F.data.startswith("category_")` + state | Категория выбрана | ⏳ |
| `parent_course_detail` | `F.data.startswith("course_detail_")` + state | Детали курса | ⏳ |
| `parent_buy_course` | `F.data.startswith("buy_course_")` + state | Покупка курса | ⏳ |
| `parent_tariff_selected` | `F.data.startswith("tariff_")` + state | Тариф выбран | ⏳ |
| `back_to_parent_menu` | `F.data == "back_to_parent_menu"` | Возврат в меню | ⏳ |

---

## child.py (3 handlers)

### Message Handlers
| Handler | Trigger | Описание | Статус |
|---------|---------|----------|--------|
| `show_qr` | `F.text == "📷 Показать QR"` | QR-код ребёнка | ⏳ |
| `schedule` | `F.text == "🕒 Расписание"` | Расписание ребёнка | ⏳ |
| `child_statistics` | `F.text == "📊 Моя статистика"` | Статистика ребёнка | ⏳ |

---

## Приоритеты переписывания

### Высокий приоритет (Core функционал)
1. [ ] `user.py` - каталог курсов, поиск
2. [ ] `user.py` - покупка абонементов, платежи
3. [ ] `partner.py` - регистрация центра
4. [ ] `partner.py` - сканирование QR

### Средний приоритет
5. [ ] `admin.py` - модерация центров
6. [ ] `admin.py` - управление шаблонами абонементов
7. [ ] `parent.py` - добавление детей, покупка для них
8. [ ] `user.py` - отзывы, статистика

### Низкий приоритет
9. [ ] `admin.py` - рассылки
10. [ ] `child.py` - профиль ребёнка
11. [ ] `partner.py` - аналитика, настройки

---

## Легенда статусов

| Статус | Описание |
|--------|----------|
| ✅ | Полностью переписан в app/ |
| 🔄 | Частично переписан |
| ⏳ | Ожидает переписывания |
| ❌ | Не нужен / deprecated |
