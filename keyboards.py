from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def create_confirmation_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"confirm:{user_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{user_id}"),
            ]
        ]
    )

def get_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="💞 Соединиться с партнером 💞")]],
        resize_keyboard=True
    )

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Почему я тебя люблю?")],
        [KeyboardButton(text="Приятность")],
        [KeyboardButton(text="💋")],
        [KeyboardButton(text="Статус партнера")],
        [KeyboardButton(text="Мини-игра 🎮", web_app=WebAppInfo(url="YOUR_WEB_APP_URL"))],  #  Кнопка с WebApp
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)