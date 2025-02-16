import asyncio
import os
import json  #  Импортируем json
import time # Импортируем

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from Bot_Love.handlers import router  #  Импортируем роутер
from Bot_Love.commands import schedule_daily_job, polling_stopped, running  #  Импортируем
from Bot_Love.config import get_admin_id, TOKEN, WEBAPP_HOST, WEBAPP_PORT  #  Импортируем

async def handle_click(request):
    """Обрабатывает POST-запрос с данными о нажатии."""
    try:
        data = await request.json()
        user_id = data.get('user_id')
        button_index = data.get('button_index')

        if not all([user_id, isinstance(button_index, int)]):
            raise ValueError("Invalid request data")

        timestamp = int(time.time())  #  Добавляем timestamp
        click_data = {"user_id": user_id, "button_index": button_index, "timestamp": timestamp}
        add_click(click_data) # Сохраняем

        return web.json_response({"status": "ok"})

    except (ValueError, json.JSONDecodeError) as e:
        print(f"Invalid request: {e}")
        return web.Response(status=400, text=str(e))
    except Exception as e:
        print(f"Error handling click: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def handle_get_clicks(request):
    """Обрабатывает GET-запрос на получение новых нажатий."""
    try:
        last_update = int(request.rel_url.query.get('last_update', 0))
        clicks = get_clicks(last_update)
        return web.json_response({"clicks": clicks})
    except ValueError:
        return web.Response(status=400, text="Invalid last_update value")
    except Exception as e:
        print(f"Error in handle_get_clicks: {e}")
        return web.Response(status=500, text=str(e))

# ---  Функции для работы с данными (data/clicks.json) ---

def load_clicks():
    """Загружает данные о нажатиях из файла."""
    try:
        with open("data/clicks.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"clicks": []}

def save_clicks(data):
    """Сохраняет данные о нажатиях в файл."""
    try:
        with open("data/clicks.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving clicks: {e}")

def add_click(click_data):
    """Добавляет новое нажатие в данные."""
    data = load_clicks()
    data["clicks"].append(click_data)
    save_clicks(data)

def get_clicks(last_update):
    """Возвращает нажатия, произошедшие после last_update."""
    data = load_clicks()
    new_clicks = [click for click in data["clicks"] if click["timestamp"] > last_update]
    return new_clicks

async def on_startup(app):
    """Действия при запуске приложения (перед стартом polling)."""
    os.makedirs("data", exist_ok=True)  #  Создаем папку data
    await bot.delete_webhook(drop_pending_updates=True)

async def on_shutdown(app):
    """Действия при остановке приложения."""
    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()

async def init_app() -> web.Application: # Добавлено
    """Инициализирует и возвращает aiohttp Application."""
    app = web.Application()
    #  Добавляем маршруты (routes) для веб-сервера
    app.router.add_post('/click', handle_click)  # POST-запрос для нажатия
    app.router.add_get('/get_clicks', handle_get_clicks)  # GET-запрос для обновлений
    app.router.add_static('/', path='.') # Раздача статики

    #  Настраиваем хуки aiogram (выполняются до/после polling)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app

async def main() -> None:
    """Основная функция."""

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    if get_admin_id() is None:
        print("НЕ УДАЛОСЬ ЗАПУСТИТЬ БОТА: Не установлен ADMIN_ID.")
        return

    asyncio.create_task(schedule_daily_job()) # Запускаем таск

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        while not polling_stopped:
            await dp.start_polling(bot)
    except TelegramBadRequest as e:
        if "bot has already been closed" in str(e):
            print("Ошибка: Бот был закрыт ранее. Повторный запуск невозможен.")
        else:
            print(f"TelegramBadRequest: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    app = asyncio.run(init_app()) # Создаём aiohttp приложение
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT) # Запускаем aiohttp сервер