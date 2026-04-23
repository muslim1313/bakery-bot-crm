# states.py
from aiogram.fsm.state import State, StatesGroup

class OrderForm(StatesGroup):
    choosing_product = State()
    choosing_payment = State()
