def is_admin(user_id: int) -> bool:
    from .config import get_admin_id  #  Импортируем здесь
    return user_id == get_admin_id()