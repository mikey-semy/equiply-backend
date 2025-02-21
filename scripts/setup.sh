#!/bin/bash

# Определяем цвета
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m' # Без цвета

# Проверяем наличие uv
if ! command -v uv &> /dev/null; then
    echo -e "${CYAN}📥 Устанавливаю uv...${NC}"
    pip install uv
    echo -e "${GREEN}✅ uv установлен!${NC}"
fi

# Проверяем наличие .venv
if [ ! -d ".venv" ]; then
    echo -e "${CYAN}🚀 Создаю виртуальное окружение...${NC}"
    uv venv
    echo -e "${GREEN}✨ Виртуальное окружение создано!${NC}"

    echo -e "${CYAN}🔌 Активирую виртуальное окружение...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение активировано!${NC}"

    echo -e "${CYAN}📦 Устанавливаю зависимости...${NC}"
    uv pip install -e ".[dev]"
    echo -e "${GREEN}🎉 Установка завершена успешно!${NC}"
else
    echo -e "${CYAN}🔌 Активирую виртуальное окружение...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Виртуальное окружение активировано!${NC}"
fi
