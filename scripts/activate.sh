#!/bin/bash

# Переходим в корневую директорию
cd "$(dirname "$0")/.."

# Запускаем setup.sh
./scripts/setup.sh

# Запускаем dev режим из корня
echo "🚀 Запускаю dev режим..."
uv run dev
