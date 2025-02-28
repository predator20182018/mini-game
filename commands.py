import asyncio
import datetime
import random
import sys
import os
import json

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramNotFound

from .states import Status, Connection
from .keyboards import create_confirmation_keyboard, get_start_keyboard, get_main_keyboard
from .config import start_date, moscow_tz, TOKEN, get_admin_id, WEB_APP_URL
from .utils import is_admin

bot = Bot(token=TOKEN)

# Словари для хранения данных
user_data = {}        # {chat_id: username}
user_message_ids = {}  # {chat_id: message_id}
user_statuses = {}     # {chat_id: status}
connections = {}       # {user_id1: user_id2, user_id2: user_id1}
pending_requests = {} # {user_id: requester_id}


# Глобальные переменные
running = True
# polling_stopped = False  #  Убрали, достаточно running


async def send_days_together_message(user_id: int):
    """Редактирует/отправляет сообщение 'Дней вместе'."""
    try:
        if get_partner_id(user_id) is None:  # Проверяем, что соединение установлено
            return

        today = datetime.datetime.now(moscow_tz).date()
        days_diff = (today - start_date).days
        message_text = f"💖 Мы вместе уже {days_diff} дней! 💖"

        message_id = user_message_ids.get(user_id)

        if message_id:
            await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=message_text)
        else:
            sent_message = await bot.send_message(chat_id=user_id, text=message_text)
            message_id = sent_message.message_id
            user_message_ids[user_id] = message_id
            await bot.pin_chat_message(chat_id=user_id, message_id=message_id)
    except Exception as e:
        print(f"Ошибка в send_days_together_message для {user_id}: {e}")


async def start(message: Message, state: FSMContext):
    """Логика команды /start."""
    chat_id = message.chat.id
    username = message.from_user.username

    await state.clear()

    # Определяем, какую клавиатуру показывать:
    if get_partner_id(chat_id) is not None:
        reply_markup = get_main_keyboard()  # Клавиатура для соединенных
        await message.answer("Вы уже соединены с партнером. Выберите действие:", reply_markup=reply_markup)
        await send_days_together_message(chat_id)
    else:
        reply_markup = get_start_keyboard()  # Клавиатура для несоединенных
        await message.answer(
            f"Привет, {message.from_user.first_name}! Выбери действие:",
            reply_markup=reply_markup,
        )

    if username:
        user_data[chat_id] = username
        print(f"Сохранен chat_id {chat_id} для @{username} (/start)")
    else:
        print(f"Нет username у {message.from_user.first_name}, chat_id={chat_id}")


async def stop_polling(message: Message):
    """Логика остановки polling (для администратора)."""
    global running #, polling_stopped  # Убрали polling_stopped
    running = False
    # polling_stopped = True
    await bot.close()
    await message.answer("Бот остановлен (перестал принимать сообщения).")
    print("Бот остановлен командой /stop_polling")


async def stop(message: Message):
    """Логика остановки бота"""
    global running #, polling_stopped  # Убрали polling_stopped
    admin_id = get_admin_id()

    if admin_id is None:
        await message.answer("ОШИБКА: Не удалось определить ID администратора.")
        return
    if message.from_user.id == admin_id:
        running = False
        # polling_stopped = True
        await bot.close()
        await message.answer("Бот остановлен")
        print("Бот остановлен")
        sys.exit()
    else:
        await message.answer("У вас нет прав")


async def help_command(message: Message):
    """Логика команды /help."""
    help_text = (
        "Этот бот умеет:\n"
        "/start - Запустить бота\n"
        "/help - Показать справку\n"
        "/stop - Остановить бота (полностью)\n"
        "/stop_polling - Остановить приём сообщений (для администратора)\n"
        "/restart - Перезапустить бота\n"
        "/quit - Разорвать соединение с партнером\n"
        "/quit_game - Выйти из мини-игры\n"
        "Отправлять ежедневное сообщение о количестве дней вместе\n"
        "Отправлять случайные приятности и причины любви по кнопкам\n"
        "Отправлять поцелуй другому пользователю\n"
        "Устанавливать и просматривать статус партнера\n"
        "💞 Соединиться с партнером 💞 - для начала общения\n"
        "🎮 Мини-игра - начать совместную мини-игру"
    )
    await message.answer(help_text)


async def why_love(message: Message):
    user_id = message.from_user.id
    if get_partner_id(user_id) is None:
        await message.answer("Сначала соединитесь с партнером!")
        return
    try:
        #  Получаем путь к директории текущего скрипта
        current_dir = os.path.dirname(os.path.abspath(__file__))
        #  Формируем полный путь к файлу
        file_path = os.path.join(current_dir, "Причины.txt")
        with open(file_path, "r", encoding="utf-8") as f:
            reasons = f.readlines()
        reason = random.choice(reasons).strip()
        await message.answer(reason)
    except FileNotFoundError:
        await message.answer("Файл 'Причины.txt' не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при чтении 'Причины.txt': {e}")


async def pleasantness(message: Message):
    user_id = message.from_user.id
    if get_partner_id(user_id) is None:
        await message.answer("Сначала соединитесь с партнером!")
        return
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "Приятность.txt")
        with open(file_path, "r", encoding="utf-8") as f:
            pleasantnesses = f.readlines()
        pleasantness_text = random.choice(pleasantnesses).strip()
        await message.answer(pleasantness_text)
    except FileNotFoundError:
        await message.answer("Файл 'Приятность.txt' не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при чтении 'Приятность.txt': {e}")


async def kiss(message: Message):
    user_id = message.from_user.id
    partner_id = get_partner_id(user_id)

    if partner_id:
        partner_username = user_data.get(partner_id)
        sender_username = user_data.get(user_id)
        if partner_username and sender_username:
            await bot.send_message(partner_id, f"💋 Вам поцелуй от @{sender_username}!")
            await message.answer("Поцелуй отправлен! 💋")
        else:
            await message.answer("Ошибка: Не удалось определить имена пользователей.")
    else:
        await message.answer("Вы не соединены с партнером. Используйте '💞 Соединиться с партнером'.")


async def status(message: Message):
    keyboard = [
       [InlineKeyboardButton(text="Посмотреть свой статус", callback_data="show_my_status")],
       [InlineKeyboardButton(text="Посмотреть статус партнера", callback_data="show_partner_status")],
       [InlineKeyboardButton(text="Изменить свой статус", callback_data="change_my_status")],
    ]
    await message.answer("Выберите действие со статусом:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))


async def show_my_status(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    status = user_statuses.get(user_id, "Статус не установлен.")
    await callback_query.answer(text=f"Ваш статус: {status}", show_alert=True)


async def show_partner_status(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    partner_id = get_partner_id(user_id)
    if partner_id:
        partner_status = user_statuses.get(partner_id, "Статус не установлен.")
        await callback_query.answer(text=f"Статус партнера: {partner_status}", show_alert=True)
    else:
        await callback_query.answer(text="Вы не соединены с партнером.", show_alert=True)


async def change_my_status(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите новый статус:")
    await state.set_state(Status.waiting_for_status)
    await callback_query.answer()


async def set_status(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_statuses[user_id] = message.text
    await message.answer(f"Ваш статус изменен на: {message.text}")
    await state.clear()

    if get_partner_id(user_id) is not None:
        await send_days_together_message(user_id)
        reply_markup = get_main_keyboard()
        await message.answer("Выберите действие:", reply_markup=reply_markup)
    else:
        reply_markup = get_start_keyboard()
        await message.answer("Выберите действие:", reply_markup=reply_markup)


async def connect_partner(message: Message, state: FSMContext) -> None:
    await message.answer("Введите ID партнера (число):")
    await state.set_state(Connection.waiting_for_partner_id)


async def process_partner_id(message: Message, state: FSMContext) -> None:
    try:
        partner_id = int(message.text)
    except ValueError:
        await message.answer("Неверный формат ID. Введите число.")
        return

    user_id = message.from_user.id

    if user_id == partner_id:
        await message.answer("Нельзя соединиться с самим собой.")
        return

    if get_partner_id(user_id) is not None:
        await message.answer("Вы уже соединены с партнером.")
        return

    if partner_id not in user_data:
        await message.answer("Пользователь с таким ID не найден.")
        return
    await state.update_data(partner_id=partner_id) # Сохраняем
    pending_requests[partner_id] = user_id
    keyboard = create_confirmation_keyboard(user_id)

    try:
        await bot.send_message(
            partner_id,
            f"Пользователь {message.from_user.first_name} (ID: {user_id}) хочет соединиться с вами.",
            reply_markup=keyboard,
        )
        await message.answer(f"Запрос отправлен пользователю с ID {partner_id}.")

    except TelegramBadRequest:
        await message.answer(f"Не удалось отправить запрос пользователю {partner_id}.")
        if partner_id in pending_requests:
            del pending_requests[partner_id]  # Удаляем запрос, если не удалось отправить

    except Exception as e:
        print(f"Ошибка в process_partner_id: {e}")
        await message.answer("Произошла ошибка при отправке запроса.")
        if partner_id in pending_requests:
            del pending_requests[partner_id]
    finally:
        await state.clear()


async def confirm_connection(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    partner_id = int(callback_query.data.split(":")[1])

    if get_partner_id(user_id) is not None:
        await callback_query.answer("Вы уже соединены с партнером.", show_alert=True)
        return
    try:
        if pending_requests.get(user_id) != partner_id:
            raise KeyError("Несоответствие ID в запросе.")

        connections[user_id] = partner_id
        connections[partner_id] = user_id

        del pending_requests[user_id]

        await callback_query.answer("Соединение установлено!", show_alert=True)
        await bot.send_message(user_id, "Соединение установлено!")
        await bot.send_message(partner_id, "Соединение установлено!")

        # Отправляем сообщение с количеством дней вместе обоим пользователям
        await send_days_together_message(user_id)
        await send_days_together_message(partner_id)

        # Обновляем клавиатуру для обоих пользователей
        main_keyboard = get_main_keyboard()
        await bot.send_message(user_id, "Выберите действие:", reply_markup=main_keyboard)
        await bot.send_message(partner_id, "Выберите действие:", reply_markup=main_keyboard)

    except KeyError as e:
        print(f"KeyError in confirm_connection: {e}")
        await callback_query.answer("Запрос устарел или отменен.", show_alert=True)
    except Exception as e:
        print(f"confirm_connection error: {e}")
        await callback_query.answer("Произошла ошибка.", show_alert=True)
    finally:
        await state.clear()


async def reject_connection(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    partner_id = int(callback_query.data.split(":")[1])
    requester = pending_requests.get(user_id)

    await callback_query.answer("Соединение отклонено.", show_alert=True)
    await bot.send_message(user_id, "Вы отклонили запрос.")

    if user_id in pending_requests:
        del pending_requests[user_id]

    try:
        await bot.send_message(partner_id, "Ваш запрос на соединение был отклонен.")
        # Обновляем клавиатуру для *отправителя* запроса:
        await bot.send_message(partner_id, "Выберите действие:", reply_markup=get_start_keyboard())

    except TelegramBadRequest:
        print(f"Не удалось уведомить пользователя {partner_id} (заблокировал).")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")


async def quit_connection(message: Message, state: FSMContext) -> None:
    """Разрывает соединение между пользователями."""
    user_id = message.from_user.id
    partner_id = get_partner_id(user_id)

    if partner_id is None:
        await message.answer("Вы не соединены с партнером!")
        return

    # Удаляем записи из connections
    del connections[user_id]
    del connections[partner_id]

    # Отправляем сообщения
    await message.answer("Вы разорвали соединение с партнером.")
    await bot.send_message(partner_id, "Ваш партнер разорвал соединение.")

    # Очищаем состояния (на всякий случай)
    await state.clear()  # Очищаем состояние только *текущего* пользователя

    # Показываем *стартовую* клавиатуру (с кнопкой "Соединиться") *обоим*
    await message.answer("Выберите действие:", reply_markup=get_start_keyboard())
    await bot.send_message(partner_id, "Выберите действие:", reply_markup=get_start_keyboard())


async def pinned_message(message: Message):
    """Обработчик закрепленного сообщения."""
    print("Обрабатываем закрепленное сообщение")


async def other_messages(message: Message):
    await message.reply("Не понимаю команду. Используйте /connect")


def get_partner_id(user_id: int) -> int | None:
    return connections.get(user_id)


async def days_together_job():
    # print("**Выполняется days_together_job**")  #  Убрали для чистоты вывода
    for user_id in user_data:  #  Итерируемся по всем user_data (можно по connections)
        try:
            if get_partner_id(user_id) is not None:
                await send_days_together_message(user_id)
        except Exception as e:
            print(f"Ошибка в days_together_job для chat_id {user_id}: {e}")


async def schedule_daily_job():
    global bot, running
    """Планировщик для ежедневного запуска задачи."""
    while running:
        now = datetime.datetime.now(moscow_tz)
        target_time = datetime.time(hour=12, minute=0, tzinfo=moscow_tz)
        target_datetime = datetime.datetime.combine(now.date(), target_time)

        if now.replace(tzinfo=moscow_tz) > target_datetime:
            target_datetime += datetime.timedelta(days=1)

        interval = (target_datetime - now).total_seconds()
        await asyncio.sleep(interval)
        if running:
            await days_together_job()