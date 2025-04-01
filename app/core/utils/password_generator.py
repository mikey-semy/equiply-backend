import random
import string

def generate_secure_password(length: int = 12) -> str:
    """
    Генерирует надежный пароль, соответствующий требованиям безопасности.

    Args:
        length: Длина пароля (минимум 8)

    Returns:
        Сгенерированный пароль
    """
    if length < 8:
        length = 8  # Минимальная длина для безопасного пароля

    # Определяем наборы символов
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Убедимся, что пароль содержит как минимум по одному символу из каждой категории
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]

    # Добавляем остальные символы
    remaining_length = length - len(password)
    all_chars = lowercase + uppercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(remaining_length))

    # Перемешиваем символы
    random.shuffle(password)

    return ''.join(password)
