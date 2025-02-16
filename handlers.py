from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from .states import GameState  # добавили импорт
from aiogram.types import WebAppData

from . import commands
from .states import Status, Connection
from .keyboards import get_start_keyboard, get_main_keyboard
from .utils import is_admin
from .commands import get_partner_id, bot  # Импортируем get_partner_id

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await commands.start(message, state)


@router.message(Command("stop_polling"))
async def command_stop_polling_handler(message: Message) -> None:
    if is_admin(message.from_user.id):
        await commands.stop_polling(message)
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")


@router.message(Command("stop"))
async def command_stop_handler(message: Message) -> None:
    await commands.stop(message)


@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await commands.help_command(message)


# --- Обработчики кнопок ---

@router.message(F.text == "Почему я тебя люблю?")
async def why_love_reply_handler(message: Message) -> None:
    await commands.why_love(message)


@router.message(F.text == "Приятность")
async def pleasantness_reply_handler(message: Message) -> None:
    await commands.pleasantness(message)


@router.message(F.text == "💋")
async def kiss_reply_handler(message: Message) -> None:
    await commands.kiss(message)


@router.message(F.text == "Статус партнера")
async def status_button_handler(message: Message) -> None:
    await commands.status(message)


@router.callback_query(F.data == "show_my_status")
async def show_my_status_handler(callback_query: CallbackQuery) -> None:
    await commands.show_my_status(callback_query)


@router.callback_query(F.data == "show_partner_status")
async def show_partner_status_handler(callback_query: CallbackQuery) -> None:
    await commands.show_partner_status(callback_query)


@router.callback_query(F.data == "change_my_status")
async def change_my_status_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    await commands.change_my_status(callback_query, state)


@router.message(Status.waiting_for_status)
async def set_status(message: Message, state: FSMContext) -> None:
    await commands.set_status(message, state)


@router.message(F.text == "💞 Соединиться с партнером 💞")
async def connect_partner_handler(message: Message, state: FSMContext) -> None:
    await commands.connect_partner(message, state)


@router.message(Connection.waiting_for_partner_id)
async def process_partner_id(message: Message, state: FSMContext) -> None:
    await commands.process_partner_id(message, state)


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_connection(callback_query: CallbackQuery, state: FSMContext) -> None:
    await commands.confirm_connection(callback_query, state)


@router.callback_query(F.data.startswith("reject:"))
async def reject_connection(callback_query: CallbackQuery, state: FSMContext) -> None:
    await commands.reject_connection(callback_query, state)


@router.message(Command("quit"))
async def quit_command_handler(message: Message, state: FSMContext) -> None:
    await commands.quit_connection(message, state)


@router.message(F.content_type.in_(["pinned_message"]))
async def pinned_message_handler(message: Message) -> None:
    await commands.pinned_message(message)


@router.message(F.text == "Мини-игра 🎮")  # Добавили
async def start_mini_game(message: Message, state: FSMContext):
    """Обработчик для кнопки 'Мини-игра 🎮'."""
    user_id = message.from_user.id
    partner_id = get_partner_id(user_id)

    if partner_id is None:
        await message.answer("Сначала соединитесь с партнером!")
        return

    #  Переводим пользователя в состояние игры
    await state.set_state(GameState.playing)
    await message.answer(
        "Мини-игра началась! Касайтесь экрана, и ваш партнер увидит ваши касания.\n"
        "Чтобы выйти из игры, нажмите /quit_game."
    )


@router.message(GameState.playing)  # Добавили
async def handle_touches(message: Message, state: FSMContext):
    user_id = message.from_user.id
    partner_id = get_partner_id(user_id)

    if partner_id is None:
        await message.answer("Игра завершена. Вы не соединены с партнером.")
        await state.clear()
        return
    #  Предположим, что сообщение содержит координаты касания (например, "x:100 y:200")
    touch_data = message.text

    # Отправляем данные партнеру
    await bot.send_message(partner_id, f"Касание от партнера: {touch_data}")


@router.message(Command("quit_game"))  # Добавили
async def quit_game(message: Message, state: FSMContext):
    """Обработчик команды /quit_game для выхода из мини-игры."""
    current_state = await state.get_state()

    # Проверяем, находится ли пользователь в состоянии игры
    if current_state == GameState.playing:
        await message.answer("Игра завершена. Вы вышли из мини-игры.")
        await state.clear()  # Очищаем состояние игры
    else:
        await message.answer("Вы не в игре. Начните игру, нажав 'Мини-игра 🎮'.")


@router.message()
async def handle_all_other_messages(message: Message) -> None:
    await commands.other_messages(message)


@router.message(F.web_app_data)  # Добавили обработчик Web App Data
async def handle_web_app_data(message: Message):
    """Обработчик данных от мини-приложения."""
    user_id = message.from_user.id
    partner_id = get_partner_id(user_id)

    if partner_id is None:
        await message.answer("Сначала соединитесь с партнером!")
        return

    # Получаем данные от мини-приложения
    data = message.web_app_data.data
    # Отправляем данные партнеру
    await bot.send_message(partner_id, f"Данные от партнера: {data}")