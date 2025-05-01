from app.models.v1.modules.ai import ModelType


class ModelPricingCalculator:
    """
    Калькулятор стоимости использования моделей
    """

    # Цены в формате (юниты, цена в рублях за 1000 токенов)
    PRICING = {
        ModelType.YANDEX_GPT_LITE: (1, 0.20),
        ModelType.YANDEX_GPT_PRO: (6, 1.20),
        ModelType.YANDEX_GPT_PRO_32K: (6, 1.20),
        ModelType.LLAMA_8B: (1, 0.20),
        ModelType.LLAMA_70B: (6, 1.20),
        ModelType.CUSTOM: (6, 1.20),  # По умолчанию как для дорогой модели
    }

    @classmethod
    def get_price_per_1000_tokens(cls, model_type: ModelType) -> float:
        """
        Возвращает цену за 1000 токенов для указанной модели

        Args:
            model_type: Тип модели

        Returns:
            float: Цена за 1000 токенов в рублях
        """
        _, price = cls.PRICING.get(model_type, (6, 1.20))
        return price

    @classmethod
    def calculate_cost(cls, model_type: ModelType, tokens: int) -> float:
        """
        Рассчитывает стоимость использования модели

        Args:
            model_type: Тип модели
            tokens: Количество токенов

        Returns:
            float: Стоимость в рублях
        """
        price_per_1000 = cls.get_price_per_1000_tokens(model_type)
        return (tokens / 1000) * price_per_1000

    @classmethod
    def get_model_display_name(cls, model_type: ModelType) -> str:
        """
        Возвращает отображаемое имя модели

        Args:
            model_type: Тип модели

        Returns:
            str: Отображаемое имя модели
        """
        model_display_names = {
            ModelType.YANDEX_GPT_LITE: "YandexGPT Lite",
            ModelType.YANDEX_GPT_PRO: "YandexGPT Pro",
            ModelType.YANDEX_GPT_PRO_32K: "YandexGPT Pro 32K",
            ModelType.LLAMA_8B: "Llama 8B",
            ModelType.LLAMA_70B: "Llama 70B",
            ModelType.CUSTOM: "Кастомная модель",
        }

        return model_display_names.get(model_type, "Неизвестная модель")
