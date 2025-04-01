"""
Модуль для генерации уникальных имен пользователей.
"""

import random
from enum import Enum
from typing import List

from app.core.integrations.http.ai import AIHttpClient
from app.models import ModelType
from app.schemas import AIRequestSchema, CompletionOptionsSchema, MessageRole, MessageSchema


class UsernameTheme(str, Enum):
    """Темы для генерации имен пользователей"""
    SPACE = "space"
    FANTASY = "fantasy"
    MOVIES = "movies"
    GAMES = "games"
    ANIMALS = "animals"
    SCIENCE = "science"
    RANDOM = "random"


# Словарь с запасными именами по категориям на случай недоступности AI
FALLBACK_USERNAMES = {
    UsernameTheme.SPACE: [
        "cosmic_voyager", "star_gazer", "nebula_rider", "galaxy_explorer",
        "astro_nomad", "lunar_walker", "solar_surfer", "orbit_drifter"
    ],
    UsernameTheme.FANTASY: [
        "dragon_whisperer", "magic_weaver", "shadow_blade", "mystic_sage",
        "rune_keeper", "spell_binder", "elven_archer", "wizard_king"
    ],
    UsernameTheme.MOVIES: [
        "cinema_buff", "film_fanatic", "reel_master", "scene_stealer",
        "director_cut", "action_hero", "plot_twister", "silver_screen"
    ],
    UsernameTheme.GAMES: [
        "pixel_warrior", "level_master", "boss_slayer", "game_legend",
        "quest_hunter", "loot_finder", "high_scorer", "controller_king"
    ],
    UsernameTheme.ANIMALS: [
        "swift_fox", "mighty_eagle", "silent_panther", "wise_owl",
        "loyal_wolf", "fierce_tiger", "clever_raven", "brave_lion"
    ],
    UsernameTheme.SCIENCE: [
        "quantum_mind", "data_wizard", "code_crafter", "tech_guru",
        "neural_network", "algorithm_ace", "byte_master", "logic_genius"
    ],
    UsernameTheme.RANDOM: [
        "creative_spark", "bold_explorer", "curious_mind", "vibrant_soul",
        "hidden_gem", "bright_idea", "wild_card", "unique_vision"
    ]
}


# Промпты для генерации имен по категориям
THEME_PROMPTS = {
    UsernameTheme.SPACE: (
        "Сгенерируй 5 уникальных имен пользователей на персонажей из космической тематики. "
        "Используй персонажей из научной фантастики. Имена должны быть на английском, "
        "состоять из 1-2 слов, разделенных подчеркиванием, без пробелов и спецсимволов. "
        "Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.FANTASY: (
        "Сгенерируй 5 уникальных имен пользователей на персонажей из фэнтезийную тематику. "
        "Используй персонажей из мифологии, фэнтезийных миров, магии или средневековья. "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.MOVIES: (
        "Сгенерируй 5 уникальных имен пользователей на персонажей из фильмов. "
        "Используй персонажей из киноиндустрии, названия известных фильмов или имена персонажей. "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.GAMES: (
        "Сгенерируй 5 уникальных имен пользователей на игровую тематику. "
        "Используй персонажей из видеоигр, названия игровых персонажей главных или второстепенных "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.ANIMALS: (
        "Сгенерируй 5 уникальных имен пользователей на тему животных. "
        "Используй названия животных с прилагательными, описывающими их качества. "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.SCIENCE: (
        "Сгенерируй 5 уникальных имен пользователей на научную тематику. "
        "Используй персонажей из науки, технологий, программирования или математики. "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    ),
    UsernameTheme.RANDOM: (
        "Сгенерируй 5 уникальных и креативных имен пользователей. "
        "Они должны быть запоминающимися, интересными и оригинальными. "
        "Имена должны быть на английском, состоять из 1-2 слов, разделенных подчеркиванием, "
        "без пробелов и спецсимволов. Верни только список имен, каждое с новой строки."
    )
}


class UsernameGenerator:
    """
    Класс для генерации уникальных имен пользователей с использованием AI.

    Attributes:
        http_client: HTTP клиент для работы с AI API
    """

    def __init__(self):
        self.http_client = AIHttpClient()

    async def generate_username_with_ai(
        self,
        theme: UsernameTheme = UsernameTheme.RANDOM,
        model_type: ModelType = ModelType.YANDEX_GPT_LITE
    ) -> List[str]:
        """
        Генерирует список имен пользователей с использованием AI.

        Args:
            theme: Тема для генерации имен
            model_type: Тип модели AI

        Returns:
            List[str]: Список сгенерированных имен
        """
        from app.core.settings import settings

        prompt = THEME_PROMPTS.get(theme, THEME_PROMPTS[UsernameTheme.RANDOM])

        # Создаем сообщение для AI
        system_message = MessageSchema(
            role=MessageRole.SYSTEM.value,
            text="Ты генератор креативных имен пользователей. Отвечай только списком имен."
        )

        user_message = MessageSchema(
            role=MessageRole.USER.value,
            text=prompt
        )

        request = AIRequestSchema(
            modelUri=settings.yandex_model_uri,
            completionOptions=CompletionOptionsSchema(
                maxTokens=settings.YANDEX_MAX_TOKENS,
                temperature=settings.YANDEX_TEMPERATURE
            ),
            messages=[system_message, user_message],
        )

        try:
            # Отправляем запрос к AI
            response = await self.http_client.get_completion(request)

            if response.success and response.result.alternatives:
                # Извлекаем текст ответа
                text = response.result.alternatives[0].message.text

                # Разбиваем текст на строки и фильтруем пустые
                usernames = [name.strip() for name in text.split('\n') if name.strip()]

                # Удаляем возможные маркеры списка и другие артефакты
                usernames = [name.lstrip('- *').strip() for name in usernames]

                # Возвращаем только имена, которые соответствуют формату
                valid_usernames = []
                for name in usernames:
                    # Проверяем формат имени (только буквы, цифры и подчеркивания)
                    if name and all(c.isalnum() or c == '_' for c in name):
                        valid_usernames.append(name.lower())

                return valid_usernames if valid_usernames else FALLBACK_USERNAMES[theme]

            return FALLBACK_USERNAMES[theme]

        except Exception:
            # В случае ошибки используем запасные имена
            return FALLBACK_USERNAMES[theme]

    def get_fallback_username(self, theme: UsernameTheme = UsernameTheme.RANDOM) -> str:
        """
        Возвращает случайное имя из запасного списка.

        Args:
            theme: Тема для генерации имени

        Returns:
            str: Случайное имя пользователя
        """
        usernames = FALLBACK_USERNAMES.get(theme, FALLBACK_USERNAMES[UsernameTheme.RANDOM])
        # Выбираем случайное имя из списка
        username = random.choice(usernames)
        # Добавляем случайное число для уникальности
        random_number = random.randint(1000, 9999)
        return f"{username}_{random_number}"
