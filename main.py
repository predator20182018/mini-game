import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from Bot_Love.handlers import router
from Bot_Love.commands import schedule_daily_job, polling_stopped, running
from Bot_Love.config import get_admin_id, TOKEN

async def main() -> None:
    """Основная функция."""

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    if get_admin_id() is None:
        print("НЕ УДАЛОСЬ ЗАПУСТИТЬ БОТА: Не установлен ADMIN_ID.")
        return

    asyncio.create_task(schedule_daily_job())

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
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен (штатное завершение).")