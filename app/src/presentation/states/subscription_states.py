from aiogram.fsm.state import State, StatesGroup


class SubscriptionStates(StatesGroup):
    waiting_for_child_selection = State()
    waiting_for_tariff_selection = State()
