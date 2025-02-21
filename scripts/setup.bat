@echo off
chcp 65001 > nul

where uv >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo 📥 Устанавливаю uv...
    pip install uv
    echo ✅ uv установлен!
)

IF NOT EXIST ".venv" (
    echo 🚀 Создаю виртуальное окружение...
    uv venv
    echo ✨ Виртуальное окружение создано!

    echo 🔌 Активирую виртуальное окружение...
    call .\.venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано!

    echo 📦 Устанавливаю зависимости...
    uv pip install -e ".[dev]"
    echo 🎉 Установка завершена успешно!
) ELSE (
    echo 🔌 Активирую виртуальное окружение...
    call .\.venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано!
)
