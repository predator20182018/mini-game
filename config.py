import os
from dotenv import load_dotenv
import datetime

load_dotenv()

TOKEN = os.environ.get("TG_TOKEN")

def get_admin_id() -> int | None:
    """Получает ID администратора из переменной окружения."""
    try:
        admin_id_str = os.environ.get("ADMIN_ID")
        if admin_id_str is None:
            print("ОШИБКА: Переменная окружения ADMIN_ID не установлена.")
            return None
        return int(admin_id_str)
    except ValueError:
        print("ОШИБКА: ADMIN_ID должна быть числом.")
        return None

start_date = datetime.date(2024, 4, 13)  # Дата отсчета "Дней вместе"
moscow_tz = datetime.timezone(datetime.timedelta(hours=3))  # Часовой пояс