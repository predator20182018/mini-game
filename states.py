from aiogram.fsm.state import State, StatesGroup

class Status(StatesGroup):
    waiting_for_status = State()

class Connection(StatesGroup):
    waiting_for_partner_id = State()
    waiting_for_confirmation = State()

class GameState(StatesGroup):
    playing = State()  # Состояние игры