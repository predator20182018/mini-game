def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором."""
    from .config import get_admin_id  #  Импортируем здесь, чтобы избежать кольцевого импорта
    return user_id == get_admin_id()