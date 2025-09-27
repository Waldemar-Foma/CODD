# ER-диаграмма базы данных - ЦОДД Смоленск
#### Данная диаграмма показывает сущности, атрибуты и связи между таблицами базы данных.

### Чтобы открыть диаграмму на весь экран, нажмите на иконку "⭤ "  в правой части экрана.


```mermaid
erDiagram
    USERS {
        int id PK "Идентификатор"
        string username "Логин"
        string email "Email"
        string password_hash "Хэш пароля"
        boolean is_admin "Администратор"
        datetime created_at "Дата регистрации"
    }
    
    TICKETS {
        int id PK "Идентификатор"
        string title "Заголовок"
        text description "Описание"
        string location "Местоположение"
        float lat "Широта"
        float lng "Долгота"
        string status "Статус"
        string priority "Приоритет"
        int user_id FK "Автор"
        datetime created_at "Дата создания"
    }
    
    COMMENTS {
        int id PK "Идентификатор"
        text content "Текст"
        boolean is_internal "Внутренний"
        int user_id FK "Автор"
        int ticket_id FK "Заявка"
        datetime created_at "Дата создания"
    }
    
    NEWS {
        int id PK "Идентификатор"
        string title "Заголовок"
        text content "Содержание"
        boolean active "Активна"
        datetime created_at "Дата публикации"
    }
    
    SERVICES {
        int id PK "Идентификатор"
        string name "Название"
        text description "Описание"
        float price "Стоимость"
        boolean is_commercial "Коммерческая"
        boolean active "Активна"
    }

    USERS ||--o{ TICKETS : creates
    USERS ||--o{ COMMENTS : writes
    TICKETS ||--o{ COMMENTS : contains
