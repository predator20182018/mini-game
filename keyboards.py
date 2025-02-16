from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import WebAppInfo


def create_confirmation_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения соединения."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"confirm:{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{user_id}"),
            ]
        ]
    )

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Создает стартовую клавиатуру (только с кнопкой соединения)."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="💞 Соединиться с партнером 💞")]],
        resize_keyboard=True
    )

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру без кнопки 'Соединиться с партнером'."""
    keyboard = [
        [KeyboardButton(text="Почему я тебя люблю?"), KeyboardButton(text="Приятность")],
        [KeyboardButton(text="💋")],
        [KeyboardButton(text="Статус партнера")],
        [KeyboardButton(
            text="Мини-игра 🎮",
            web_app=WebAppInfo(url="https://predator20182018.github.io/mini-game/mini_game.html")  # Укажите URL вашего мини-приложения
        )],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)