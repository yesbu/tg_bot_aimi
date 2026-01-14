from aiogram.fsm.state import State, StatesGroup


class ParentStates(StatesGroup):
    waiting_for_child_name = State()
    waiting_for_child_age = State()
    selecting_child_for_subscription = State()
