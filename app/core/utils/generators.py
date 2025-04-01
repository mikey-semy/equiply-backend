import random
import string
from typing import List

def generate_username(prefix: str = "user") -> str:
    """
    Генерирует случайное имя пользователя с указанным префиксом.
    
    Args:
        prefix: Префикс для имени пользователя
        
    Returns:
        Сгенерированное имя пользователя
    """
    # Генерируем случайное число от 1000 до 9999
    random_number = random.randint(1000, 9999)
    return f"{prefix}_{random_number}"

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
