# Equiply

## Описание проекта

**Equiply** — это современная система управления оборудованием, предназначенная для автоматизации процессов обслуживания и оптимизации работы с техническими средствами. Наша платформа помогает эффективно управлять, обслуживать и применять оборудование в различных сферах.

## Установка

Клонируйте репозиторий в директорию, в которой находитесь:
```bash
git clone https://github.com/mikey-semy/equiply-backend.git .
```
Или:
```bash
git clone https://github.com/mikey-semy/equiply-backend.git
```
Перейдите в директорию с проектом:
```bash
cd ./equiply-backend
```

> [!NOTE]
> Перед тем, как запускать проект, проверьте наличие файла `.env`

## Первый запуск

`PowerShell`
```bash
.\scripts\activate.ps1
```

## Последующий запуск

Для активации виртуального окружения без запуска режима разработки:

`PowerShell`
```bash
.\scripts\setup.ps1
```

Запуск в режиме разработки (с hot-reload)
```bash
uv run dev
```

Или запуск в режиме разработки (с hot-reload)   одной командой:

`PowerShell`
```bash
.\scripts\activate.ps1
```

## Разработка

### Процесс разработки такой:
- Разработка идёт от `dev`
- В dev мерджим фичи
- Тестим на `dev`
- Когда всё ок - мерджим `dev` в main

Если вы хотите внести изменения или улучшения, пожалуйста, следуйте этим шагам:

1. Переключаемся на `dev` и подтягиваем последние изменения с удалённого репозитория:
```bash
git checkout dev
git pull origin dev
```

2. От `dev` создаем свою ветку разработки и сразу на неё переключаемся:
```bash
git checkout -b feature/your-name-of-feature
```

3. Кодим и по итогу добавляем все изменения в индекс:
```bash
git add .
```

4. Создаём коммит с описанием изменений
```bash
git commit -m "feat: your-changes"
```

5. Перед пушем обновляем ветку от `dev`, то есть
 1) Переключаемся обратно на dev
 2) Подтягиваем новые изменения
 3) Возвращаемся на свою ветку
 4) Переносим свои изменения поверх последней версии `dev`

```bash
git checkout dev
git pull origin dev
git checkout feature/your-name-of-feature
git rebase dev
```

6. Отправляем свою ветку в удалённый репозиторий:
```bash
git push origin feature/your-name-of-feature --force-with-lease
```

7. Создаем Pull Request в dev ветку!
> 1) Жмём кнопку "New Pull Request"
> 2) В base выбираем `dev` (КУДА льём)
> 3) В compare выбираем свою ветку feature/your-name-of-feature (ОТКУДА льём)
> 4) Пишешь нормальное описание что сделали
> 5) Добавляем ревьюеров
> 6) Создаёи PR

Либо просто делаем merge в dev ветку из своей feature/your-name-of-feature ветки.
```bash
git checkout dev
git merge feature/your-name-of-feature
```

8. После тестирования на `dev`, создаём PR из `dev` в `main`.
> 1) Создаём новый PR
> 2) В base выбираем main (КУДА льём)
> 3) В compare выбираем dev (ОТКУДА льём)
> 4) Описываем все изменения которые войдут в прод
> 6) Ждём подтверждения от тимлида

Либо просто делаем merge в main ветку из dev ветки.
```bash
git checkout main
git merge dev
```

9. Удаляем свою ветку feature/your-name-of-feature

Локально:

```bash
git branch -d feature/your-name-of-feature
```
Удалённо:
```bash
git push origin --delete feature/your-name-of-feature
```

## Контакты
Если у вас есть вопросы или предложения, вы можете обратиться по адресу telegram: [@mikey_semi](https://t.me/mikey_semi).

Спасибо за интерес к проекту Equiply!

Мы надеемся, что эта документация поможет вам начать работу и внести свой вклад в развитие платформы.