from aiogram.fsm.state import State, StatesGroup


class PaymentStates(StatesGroup):
    waiting_for_payment_confirmation = State()
    waiting_for_payment_check = State()
