from aiogram.fsm.state import State, StatesGroup


class AdminModerationStates(StatesGroup):
    reviewing_center = State()
    rejection_reason = State()


class SubscriptionTemplateStates(StatesGroup):
    waiting_for_template_name = State()
    waiting_for_template_lessons = State()
    waiting_for_template_price = State()
    waiting_for_template_duration = State()


class BroadcastStates(StatesGroup):
    waiting_for_broadcast_message = State()
    confirming_broadcast = State()
