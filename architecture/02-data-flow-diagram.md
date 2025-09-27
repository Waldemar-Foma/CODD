# Диаграмма потоков данных (DFD) - ЦОДД Смоленск
#### Данная диаграмма показывает потоки данных между компонентами системы, процессами обработки и внешними сущностями.

### Чтобы открыть диаграмму на весь экран, нажмите на иконку "⭤ "  в правой части экрана.

```mermaid
graph LR
    A[ГРАЖДАНИН] -->|1. Регистрация/Логин| B[ФОРМА АУТЕНТИФИКАЦИИ]
    A -->|2. Создание заявки| C[ФОРМА ОБРАЩЕНИЯ]
    A -->|3. Просмотр карты| D[КАРТА ДОРОЖНОЙ СИТУАЦИИ]
    
    B -->|Валидация данных| E[БАЗА ДАННЫХ]
    C -->|Сохранение заявки| E
    D -->|Запрос данных| E
    
    F[АДМИНИСТРАТОР] -->|4. Изменение статуса| G[ПАНЕЛЬ УПРАВЛЕНИЯ]
    F -->|5. Команды бота| H[TELEGRAM BOT]
    
    G -->|Обновление статуса| E
    H -->|Опрос новых заявок| E
    E -->|Уведомления| H
    H -->|Оповещения| F
    
    I[YANDEX MAPS API] -->|Геоданные| D
    D -->|Визуализация| A
    
    E -->|Статистика| J[АНАЛИТИЧЕСКАЯ ПАНЕЛЬ]
    J -->|Графики/Отчёты| F

    style A fill:#000000,stroke:#ffffff,color:#ffffff
    style F fill:#000000,stroke:#ffffff,color:#ffffff
    style B fill:#333333,stroke:#ffffff,color:#ffffff
    style C fill:#333333,stroke:#ffffff,color:#ffffff
    style D fill:#333333,stroke:#ffffff,color:#ffffff
    style G fill:#333333,stroke:#ffffff,color:#ffffff
    style H fill:#333333,stroke:#ffffff,color:#ffffff
    style J fill:#333333,stroke:#ffffff,color:#ffffff
    style E fill:#000000,stroke:#ffffff,color:#ffffff,stroke-width:3px
    style I fill:#000000,stroke:#ffffff,color:#ffffff
    
    linkStyle default stroke:#ffffff,stroke-width:2px
