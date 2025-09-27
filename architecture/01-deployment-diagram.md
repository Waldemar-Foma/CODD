# Диаграмма развертывания архитектуры - ЦОДД Смоленск
### Чтобы открыть диаграмму на весь экран, нажмите на иконку "⭤ "  в правой части экрана.


```mermaid
graph TD
    A[ПОЛЬЗОВАТЕЛЬ] -->|HTTP/HTTPS| B[FLASK APPLICATION]
    C[АДМИНИСТРАТОР] -->|Telegram API| D[TELEGRAM BOT]
    E[YANDEX MAPS] -->|JSON API| B
    
    B -->|SQLAlchemy| F[(SQLITE DATABASE)]
    D -->|SQLite Driver| F
    
    subgraph SG1 ["FLASK APPLICATION"]
        B1[Главные страницы]
        B2[Аутентификация]
        B3[API endpoints]
    end
    
    subgraph SG2 ["TELEGRAM BOT"]
        D1[Команды /start]
        D2[Управление заявками] 
        D3[Администрирование]
    end
    
    subgraph SG3 ["DATA"]
        F1[Таблица: users]
        F2[Таблица: tickets]
        F3[Таблица: comments]
        F4[Таблица: news]
        F5[Таблица: services]
    end
    
    B --> B1
    B --> B2
    B --> B3
    
    D --> D1
    D --> D2
    D --> D3
    
    F --> F1
    F --> F2
    F --> F3
    F --> F4
    F --> F5
    
    style A fill:#000000,stroke:#ffffff,color:#ffffff
    style C fill:#000000,stroke:#ffffff,color:#ffffff
    style E fill:#000000,stroke:#ffffff,color:#ffffff
    style B fill:#000000,stroke:#ffffff,color:#ffffff
    style D fill:#000000,stroke:#ffffff,color:#ffffff
    style F fill:#000000,stroke:#ffffff,color:#ffffff
    style B1 fill:#333333,stroke:#ffffff,color:#ffffff
    style B2 fill:#333333,stroke:#ffffff,color:#ffffff
    style B3 fill:#333333,stroke:#ffffff,color:#ffffff
    style D1 fill:#333333,stroke:#ffffff,color:#ffffff
    style D2 fill:#333333,stroke:#ffffff,color:#ffffff
    style D3 fill:#333333,stroke:#ffffff,color:#ffffff
    style F1 fill:#333333,stroke:#ffffff,color:#ffffff
    style F2 fill:#333333,stroke:#ffffff,color:#ffffff
    style F3 fill:#333333,stroke:#ffffff,color:#ffffff
    style F4 fill:#333333,stroke:#ffffff,color:#ffffff
    style F5 fill:#333333,stroke:#ffffff,color:#ffffff
    
    style SG1 fill:#000000,stroke:#ffffff,color:#ffffff
    style SG2 fill:#000000,stroke:#ffffff,color:#ffffff
    style SG3 fill:#000000,stroke:#ffffff,color:#ffffff
    
    linkStyle default stroke:#ffffff,stroke-width:2px
