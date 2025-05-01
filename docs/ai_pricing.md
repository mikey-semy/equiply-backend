Более точный расчет токенов
Для более точного расчета токенов можно использовать библиотеку tiktoken от OpenAI или другие токенизаторы.

Вот пример реализации:
```python
import re
from typing import Optional

class SimpleTokenizer:
    """
    Простой токенизатор для примерной оценки количества токенов
    """

    @staticmethod
    def count_tokens(text: str) -> int:
        """
        Примерно оценивает количество токенов в тексте

        Args:
            text: Текст для оценки

        Returns:
            int: Примерное количество токенов
        """
        # Простая эвристика: слова + пунктуация + эмодзи
        words = re.findall(r'\b\w+\b', text)
        punctuation = re.findall(r'[^\w\s]', text)

        # Примерная оценка: каждое слово ~= 1.3 токена, пунктуация ~= 1 токен
        return int(len(words) * 1.3 + len(punctuation))

# Если установлен tiktoken, можно использовать его для более точной оценки
try:
    import tiktoken

    class TiktokenTokenizer:
        """
        Токенизатор на основе tiktoken для точной оценки количества токенов
        """

        @staticmethod
        def count_tokens(text: str, model: Optional[str] = "gpt-3.5-turbo") -> int:
            """
            Точно оценивает количество токенов в тексте

            Args:
                text: Текст для оценки
                model: Модель для токенизации

            Returns:
                int: Количество токенов
            """
            try:
                encoding = tiktoken.encoding_for_model(model)
                return len(encoding.encode(text))
            except Exception:
                # Если модель не поддерживается, используем cl100k_base

```