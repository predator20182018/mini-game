import asyncio
import os
import json
import time

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from Bot_Love.handlers import router
from Bot_Love.commands import schedule_daily_job, running
from Bot_Love.config import get_admin_id, TOKEN, WEBAPP_HOST, WEBAPP_PORT


async def handle_click(request):
    """Обрабатывает POST-запрос с данными о нажатии."""
    try:
        data = await request.json()
        user_id = data.get('user_id')
        button_index = data.get('button_index')

        if not all([user_id, isinstance(button_index, int)]):
            raise ValueError("Invalid request data")

        timestamp = int(time.time())
        click_data = {"user_id": user_id, "button_index": button_index, "timestamp": timestamp}
        add_click(click_data)

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
    os.makedirs("data", exist_ok=True)
    bot = app['bot']  # Теперь bot доступен
    await bot.delete_webhook(drop_pending_updates=True)



async def on_shutdown(app):
    """Действия при остановке приложения."""
    bot = app['bot']
    dp = app['dp']
    runner = app['runner']  # Получаем runner из app
    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await runner.cleanup()  # Корректно закрываем runner



async def init_app() -> web.Application:
    """Инициализирует и возвращает aiohttp Application."""
    # Создаем bot и dp
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    # Создаем приложение и добавляем маршруты
    app = web.Application()
    app.router.add_post('/click', handle_click)
    app.router.add_get('/get_clicks', handle_get_clicks)
    app.router.add_static('/', path='.')

    # Сохраняем bot и dp в app
    app['bot'] = bot
    app['dp'] = dp

    # Добавляем обработчики событий до "заморозки"
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Настраиваем и запускаем AppRunner
    runner = web.AppRunner(app)
    app['runner'] = runner  # Сохраняем runner в app до setup()
    await runner.setup()

    # Запускаем веб-приложение
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    return app



async def run_web_app(app):
    """Запускает aiohttp приложение в том же цикле событий."""
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        print(f"Web app слушает на {WEBAPP_HOST}:{WEBAPP_PORT}")
    except Exception as e:
        print(f"Ошибка при запуске веб-приложения: {e}")


async def main() -> None:
    if get_admin_id() is None:
        print("НЕ УДАЛОСЬ ЗАПУСТИТЬ БОТА: Не установлен ADMIN_ID.")
        return

    app = await init_app()  # Инициализируем приложение

    try:
        dp = app['dp']
        bot = app['bot']  # Получаем bot из app, а не глобально
        await dp.start_polling(bot)
    except TelegramBadRequest as e:
        if "bot has already been closed" in str(e):
            print("Ошибка: Бот был закрыт ранее. Повторный запуск невозможен.")
        else:
            print(f"TelegramBadRequest: {e}")
    except KeyboardInterrupt:
        print("Бот остановлен вручную (Ctrl+C).")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Очищаем ресурсы
        await on_shutdown(app)

if __name__ == "__main__":
    asyncio.run(main())