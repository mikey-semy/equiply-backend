## 📋 ТАБЛИЦА ИСПОЛЬЗОВАНИЯ СХЕМ:

| Схема | Назначение | Endpoints | Поля |
| ------ | ------ | ------ | ------ |
| `UserSchema` | Полная схема для внутренних операций | BaseEntityManager, сервисы | Все поля модели (25+ полей) |
| `UserPrivateSchema` | Профиль владельца аккаунта | `GET /profile`, `GET /users/me` | Наследует все поля UserSchema |
| `UserPublicSchema` | Публичный профиль для других | `GET /users/{id}`, `GET /users` | username, avatar, role, is_active, total_orders |
| `UserProfileSchema` | Редактирование профиля | `PUT/PATCH /profile` | Персональные данные + настройки уведомлений |
| `CurrentUserSchema` | JWT токены и зависимости | `Depends(get_current_user)` | id, username, email, role, is_active, is_verified |
| `UserCredentialsSchema` | Внутренняя аутентификация | AuthService, TokenManager | Базовые поля + hashed_password |
| `UserDetailDataSchema` | Админ-панель | `GET /admin/users/{id}` | username, email, role, статусы, статистика |
| `UserStatusDataSchema` | Онлайн статус в реальном времени | `GET /users/{id}/status`, WebSocket | is_online, last_activity |
| `UserFinancialDataSchema` | Финансовая информация | `GET /profile/finances` | balance, bonus_points, cashback_balance, total_spent |
| `UserNotificationSettingsSchema` | Настройки уведомлений | `GET/PUT /profile/notifications` | email_notifications, sms_notifications, push_notifications, marketing_consent |
| `UserStatsSchema` | Статистика и аналитика | `GET /profile/stats`, `GET /admin/users/{id}/stats` | total_orders, total_spent, last_order_date, referral_code, referred_users_count |


## ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:

### Уровни доступа:
- Публичные: `UserPublicSchema`, `UserStatusDataSchema`
- Приватные: `UserPrivateSchema`, `UserProfileSchema`, `UserFinancialDataSchema`, `UserNotificationSettingsSchema`, `UserStatsSchema`
- Административные: `UserDetailDataSchema`
- Системные: `UserSchema`, `UserCredentialsSchema`, `CurrentUserSchema`

### Безопасность:
- ❌ Никогда не возвращать: `UserCredentialsSchema` (содержит hashed_password)
- ⚠️ Только владельцу: Финансовые данные, полная статистика
- ✅ Публично доступно: Имя, аватар, роль, количество заказов