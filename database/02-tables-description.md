# Описание таблиц и принципов работы с данными - ЦОДД Смоленск

## Обзор базы данных

База данных SQLite предназначена для хранения информации о дорожных заявках, пользователях и сопутствующих данных. Архитектура БД следует принципам реляционной модели с обеспечением целостности данных.

## 📊 Ключевые таблицы базы данных

### Таблица `users` - Пользователи системы
**Назначение:** Хранение данных пользователей, аутентификация и управление доступом

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор | 1 |
| public_id | VARCHAR(36) | UNIQUE, DEFAULT (hex(randomblob(16))) | Публичный UUID для API | "a1b2c3d4-e5f6-7890-abcd-ef1234567890" |
| username | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | Логин пользователя | "ivanov_i" |
| email | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | Электронная почта | "ivanov@example.com" |
| password_hash | VARCHAR(128) | NOT NULL | Хэш пароля (Werkzeug) | "scrypt:32768:8:1$..." |
| is_admin | BOOLEAN | DEFAULT FALSE | Права администратора | TRUE |
| is_active | BOOLEAN | DEFAULT TRUE | Активность учетной записи | TRUE |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата регистрации | "2024-01-15 10:30:00" |
| last_login | DATETIME | NULL | Последний вход | "2024-01-20 14:25:00" |
| show_in_team | BOOLEAN | DEFAULT FALSE | Показ в разделе "Команда" | TRUE |
| team_order | INTEGER | DEFAULT 0 | Порядок в команде | 1 |

**Индексы:**
- `ix_users_username` - для быстрого поиска по логину
- `ix_users_email` - для быстрого поиска по email
- `ix_users_team` - для сортировки команды (`show_in_team = TRUE`)

**Бизнес-логика:**
- При создании пользователя генерируется `public_id` как UUID
- Пароль хэшируется с помощью `werkzeug.security.generate_password_hash`
- Поле `last_login` обновляется при каждой успешной аутентификации

### Таблица `tickets` - Дорожные заявки и обращения
**Назначение:** Основная бизнес-логика системы - учет дорожных проблем

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный ID заявки | 150 |
| public_id | VARCHAR(36) | UNIQUE, DEFAULT (hex(randomblob(16))) | Публичный идентификатор | "tkt_abc123def456" |
| title | VARCHAR(100) | NOT NULL | Заголовок проблемы | "Яма на проезжей части" |
| description | TEXT | NOT NULL | Подробное описание | "Глубокая яма размером 1x1м на перекрестке Ленина-Советская" |
| location | VARCHAR(200) | NULL | Текстовое описание места | "ул. Ленина, д. 15" |
| lat | FLOAT | NULL | Географическая широта | 54.782635 |
| lng | FLOAT | NULL | Географическая долгота | 32.045287 |
| status | VARCHAR(20) | DEFAULT 'new', CHECK(status IN ('new','in_progress','resolved','closed')) | Статус обработки | "in_progress" |
| priority | VARCHAR(20) | DEFAULT 'medium', CHECK(priority IN ('low','medium','high','urgent')) | Приоритет заявки | "high" |
| image_path | VARCHAR(200) | NULL | Путь к изображению | "uploads/ticket_150.jpg" |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id), NOT NULL | Автор заявки | 1 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата создания | "2024-01-20 09:15:00" |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата обновления | "2024-01-20 14:30:00" |

**Индексы:**
- `ix_tickets_status_created` - для фильтрации по статусу и дате создания
- `ix_tickets_user_created` - для поиска заявок конкретного пользователя
- `ix_tickets_priority` - для сортировки по приоритету
- `ix_tickets_location` - для поиска по местоположению

**Статусы заявок:**
- `new` - Новая (только создана)
- `in_progress` - В работе (принята специалистами)
- `resolved` - Решена (проблема устранена)
- `closed` - Закрыта (архивирована)

**Приоритеты:**
- `low` - Низкий (не влияет на движение)
- `medium` - Средний (создает неудобства)
- `high` - Высокий (затрудняет движение)
- `urgent` - Срочный (аварийная ситуация)

### Таблица `comments` - Комментарии к заявкам
**Назначение:** Обсуждение заявок, история обработки, коммуникация

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | ID комментария | 325 |
| public_id | VARCHAR(36) | UNIQUE, DEFAULT (hex(randomblob(16))) | Публичный ID | "cmt_xyz789uvw456" |
| content | TEXT | NOT NULL | Текст комментария | "Выехала бригада для осмотра" |
| is_internal | BOOLEAN | DEFAULT FALSE | Только для администраторов | TRUE |
| user_id | INTEGER | FOREIGN KEY REFERENCES users(id), NOT NULL | Автор комментария | 2 |
| ticket_id | INTEGER | FOREIGN KEY REFERENCES tickets(id), NOT NULL | Связанная заявка | 150 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата создания | "2024-01-20 11:20:00" |

**Ограничения внешнего ключа:**
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
```
# Описание таблиц и принципов работы с данными - ЦОДД Смоленск

## 📊 Структура таблицы `news` - Новости ЦОДД

**Назначение:** Публикация новостей, анонсов и официальных объявлений для граждан

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Уникальный идентификатор новости | `150` |
| `public_id` | VARCHAR(36) | UNIQUE, DEFAULT (hex(randomblob(16))) | Публичный UUID для API ссылок | `"news_abc123def456"` |
| `title` | VARCHAR(200) | NOT NULL | Заголовок новости | `"Ремонт дорог на улице Ленина"` |
| `content` | TEXT | NOT NULL | Полное содержание новости | `"С 15 января начинаются работы..."` |
| `excerpt` | VARCHAR(300) | NULL | Краткое описание для превью | `"Запланирован ремонт дорожного покрытия"` |
| `image_path` | VARCHAR(200) | NULL | Путь к изображению новости | `"uploads/news_150.jpg"` |
| `active` | BOOLEAN | DEFAULT TRUE | Флаг активности новости | `TRUE` |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата и время публикации | `"2024-01-15 10:00:00"` |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата последнего обновления | `"2024-01-16 14:30:00"` |

## 📊 Структура таблицы `services` - Услуги ЦОДД

**Назначение:** Каталог коммерческих и бесплатных услуг центра

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID услуги | `25` |
| `public_id` | VARCHAR(36) | UNIQUE | Публичный идентификатор | `"svc_xyz789uvw012"` |
| `name` | VARCHAR(100) | NOT NULL | Название услуги | `"Проектирование дорожных развязок"` |
| `description` | TEXT | NOT NULL | Описание услуги | `"Разработка проектной документации..."` |
| `price` | DECIMAL(10,2) | DEFAULT 0.00 | Стоимость услуги | `15000.00` |
| `category` | VARCHAR(50) | NULL | Категория услуги | `"projection"` |
| `is_commercial` | BOOLEAN | DEFAULT TRUE | Флаг коммерческой услуги | `TRUE` |
| `active` | BOOLEAN | DEFAULT TRUE | Активность услуги | `TRUE` |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата добавления | `"2024-01-10 09:00:00"` |

## 📊 Структура таблицы `documents` - Документы ЦОДД

**Назначение:** Хранение официальных документов для публикации

| Поле | Тип данных | Ограничения | Описание | Пример значения |
|------|------------|-------------|----------|-----------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID документа | `30` |
| `public_id` | VARCHAR(36) | UNIQUE | Публичный ID | `"doc_123abc456def"` |
| `title` | VARCHAR(200) | NOT NULL | Название документа | `"Правила дорожного движения"` |
| `description` | TEXT | NULL | Описание документа | `"Актуальная версия ПДД"` |
| `file_path` | VARCHAR(200) | NOT NULL | Путь к файлу | `"documents/pdd_2024.pdf"` |
| `category` | VARCHAR(100) | NOT NULL | Категория документа | `"official"` |
| `file_size` | INTEGER | NULL | Размер файла в байтах | `2048576` |
| `active` | BOOLEAN | DEFAULT TRUE | Активность документа | `TRUE` |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата добавления | `"2024-01-05 12:00:00"` |

## 🔧 Принципы хранения данных

### 1. Нормализация схемы базы данных

```sql
-- Третья нормальная форма (3NF) - исключение транзитивных зависимостей
-- Каждая таблица содержит только атрибуты, зависящие от первичного ключа

CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_id VARCHAR(36) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    excerpt VARCHAR(300),
    image_path VARCHAR(200),
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Отсутствие избыточности: нет дублирования данных между таблицами
-- Каждая сущность в отдельной таблице с четкими связями
```
### 2. Целостность данных через внешние ключи
```sql
-- Внешние ключи с каскадным удалением
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    -- ... другие поля ...
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ticket_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);

-- Каскадное удаление: при удалении пользователя удаляются его заявки и комментарии
-- При удалении заявки удаляются все связанные комментарии
```
### 3. Валидация доменных значений через CHECK-ограничения
```sql
-- CHECK-ограничения для валидации статусов и приоритетов
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR(20) DEFAULT 'new' 
        CHECK (status IN ('new', 'in_progress', 'resolved', 'closed')),
    priority VARCHAR(20) DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    -- ... другие поля ...
);

-- CHECK-ограничения для числовых значений
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price DECIMAL(10,2) DEFAULT 0.00
        CHECK (price >= 0),
    -- ... другие поля ...
);

-- CHECK-ограничения для булевых значений
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    active BOOLEAN DEFAULT TRUE
        CHECK (active IN (0, 1)),
    -- ... другие поля ...
);
```
### 4. Индексация для производительности
```sql
-- Составные индексы для частых запросов
CREATE INDEX ix_news_active_created ON news(active, created_at DESC);
CREATE INDEX ix_tickets_status_priority ON tickets(status, priority, created_at);
CREATE INDEX ix_services_category_active ON services(category, active);

-- Частичные индексы для оптимизации
CREATE INDEX ix_active_news ON news(created_at) WHERE active = TRUE;
CREATE INDEX ix_commercial_services ON services(price) WHERE is_commercial = TRUE;
```
### 5. Триггеры для автоматического обновления
```sql
-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_news_timestamp 
AFTER UPDATE ON news
FOR EACH ROW
BEGIN
    UPDATE news SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Триггер для генерации excerpt из content
CREATE TRIGGER generate_news_excerpt 
AFTER INSERT ON news
FOR EACH ROW
WHEN NEW.excerpt IS NULL
BEGIN
    UPDATE news SET excerpt = substr(NEW.content, 1, 300) WHERE id = NEW.id;
END;
```
### Таблица `vacancies` - Вакансии ЦОДД
| Поле | Тип данных | Ограничения | Описание |
|------|------------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID вакансии |
| `public_id` | VARCHAR(36) | UNIQUE | Публичный ID |
| `title` | VARCHAR(200) | NOT NULL | Должность |
| `description` | TEXT | NOT NULL | Описание вакансии |
| `requirements` | TEXT | NULL | Требования к кандидату |
| `salary` | VARCHAR(100) | NULL | Уровень зарплаты |
| `active` | BOOLEAN | DEFAULT TRUE | Активность вакансии |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата публикации |

### Таблица `projects` - Проекты ЦОДД
| Поле | Тип данных | Ограничения | Описание |
|------|------------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID проекта |
| `public_id` | VARCHAR(36) | UNIQUE | Публичный ID |
| `title` | VARCHAR(200) | NOT NULL | Название проекта |
| `description` | TEXT | NOT NULL | Описание проекта |
| `image_path` | VARCHAR(200) | NULL | Изображение проекта |
| `is_free` | BOOLEAN | DEFAULT TRUE | Бесплатный проект |
| `active` | BOOLEAN | DEFAULT TRUE | Активность проекта |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата создания |

### Таблица `partners` - Партнеры ЦОДД
| Поле | Тип данных | Ограничения | Описание |
|------|------------|-------------|----------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ID партнера |
| `public_id` | VARCHAR(36) | UNIQUE | Публичный ID |
| `name` | VARCHAR(100) | NOT NULL | Название организации |
| `logo_path` | VARCHAR(200) | NULL | Логотип партнера |
| `website` | VARCHAR(200) | NULL | Сайт партнера |
| `active` | BOOLEAN | DEFAULT TRUE | Активность партнера |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Дата добавления |

## 📈 Полный список индексов базы данных

| Индекс | Таблица | Поля | Назначение |
|--------|---------|------|------------|
| `ix_users_username` | `users` | `username` | Быстрый поиск по логину |
| `ix_users_email` | `users` | `email` | Быстрый поиск по email |
| `ix_users_team` | `users` | `show_in_team, team_order` | Сортировка команды |
| `ix_tickets_status_created` | `tickets` | `status, created_at` | Фильтрация по статусу и дате |
| `ix_tickets_user_created` | `tickets` | `user_id, created_at` | Заявки пользователя |
| `ix_tickets_priority` | `tickets` | `priority` | Сортировка по приоритету |
| `ix_tickets_geo` | `tickets` | `lat, lng` | Поиск по координатам |
| `ix_comments_ticket` | `comments` | `ticket_id, created_at` | Комментарии заявки |
| `ix_news_active_created` | `news` | `active, created_at` | Активные новости |
| `ix_services_category` | `services` | `category, active` | Услуги по категориям |

## 💻 Примеры реальных SQL-запросов

### 1. Получение активных заявок для карты
```sql
SELECT id, title, lat, lng, status, priority, created_at 
FROM tickets 
WHERE lat IS NOT NULL 
AND lng IS NOT NULL 
AND status IN ('new', 'in_progress')
ORDER BY created_at DESC;
```
### 2. Статистика для главной страницы
```sql
SELECT 
    COUNT(*) as total_tickets,
    SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_tickets,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_tickets,
    (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as active_users
FROM tickets;
```
### 3. Поиск заявок по местоположению
```sql
SELECT t.*, u.username 
FROM tickets t
JOIN users u ON t.user_id = u.id
WHERE t.location LIKE '%Ленина%'
AND t.status != 'closed'
ORDER BY t.created_at DESC
LIMIT 20;
```
