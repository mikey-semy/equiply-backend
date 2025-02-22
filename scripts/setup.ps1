# Устанавливаем uv если его нет
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📥 Устанавливаю uv..." -ForegroundColor Cyan
    pip install uv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Ошибка при установке uv!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ uv установлен!" -ForegroundColor Green
}

# Проверяем существование проекта
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "📦 Инициализирую Python проект..." -ForegroundColor Cyan
    uv init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Ошибка при инициализации проекта!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Проект инициализирован!" -ForegroundColor Green
}

# Проверяем существование .venv
if (-not (Test-Path ".venv")) {
    Write-Host "🚀 Создаю виртуальное окружение..." -ForegroundColor Cyan
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Ошибка при создании виртуального окружения!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✨ Виртуальное окружение создано!" -ForegroundColor Green

    Write-Host "🔌 Активирую виртуальное окружение..." -ForegroundColor Cyan
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Виртуальное окружение активировано!" -ForegroundColor Green

    Write-Host "📦 Устанавливаю зависимости..." -ForegroundColor Cyan
    uv pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Ошибка при установке зависимостей!" -ForegroundColor Red
        exit 1
    }
    Write-Host "🎉 Установка завершена успешно!" -ForegroundColor Green
}
else {
    Write-Host "🔌 Активирую виртуальное окружение..." -ForegroundColor Cyan
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Виртуальное окружение активировано!" -ForegroundColor Green
}