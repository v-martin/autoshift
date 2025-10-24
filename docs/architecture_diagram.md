# Архитектура сервисов AutoShift

## Схема взаимодействия компонентов

```mermaid
graph TB
    subgraph "Docker Environment"
        subgraph "Frontend Layer"
            NGINX[🌐 Nginx<br/>API Gateway<br/>:80, :443]
        end
        
        subgraph "Application Layer"
            DJANGO[🐍 Django App<br/>AutoShift API<br/>:8000]
            DASHBOARD[📊 Web Dashboard<br/>Bootstrap + Chart.js]
        end
        
        subgraph "Microservices"
            OPTIMIZER[⚙️ Shift Optimizer<br/>gRPC Service<br/>:50051]
        end
        
        subgraph "Data Layer"
            POSTGRES[(🐘 PostgreSQL<br/>Database<br/>:5432)]
        end
        
        subgraph "External"
            CLIENT[👤 Client Browser]
            MOBILE[📱 Mobile App<br/>(Future)]
        end
    end
    
    %% Client connections
    CLIENT -->|HTTP/HTTPS| NGINX
    MOBILE -.->|REST API| NGINX
    
    %% Nginx routing
    NGINX -->|/api/*| DJANGO
    NGINX -->|/dashboard| DJANGO
    NGINX -->|/admin| DJANGO
    NGINX -->|Static Files| DJANGO
    
    %% Django connections
    DJANGO -->|SQL Queries| POSTGRES
    DJANGO -->|gRPC Calls| OPTIMIZER
    DJANGO -->|Renders| DASHBOARD
    
    %% Internal communication
    OPTIMIZER -->|Read Data| POSTGRES
    
    %% Styling
    classDef container fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef database fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef client fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class NGINX,DJANGO,OPTIMIZER container
    class POSTGRES database
    class DASHBOARD service
    class CLIENT,MOBILE client
```

## Компоненты системы

### 1. **Nginx (API Gateway)**
- **Порт**: 80, 443
- **Функции**:
  - Обратный прокси для Django приложения
  - Обслуживание статических файлов
  - SSL терминация
  - Балансировка нагрузки
  - Кэширование

### 2. **Django Application (Backend API)**
- **Порт**: 8000
- **Функции**:
  - REST API для управления сменами
  - Аутентификация и авторизация (JWT)
  - Бизнес-логика приложения
  - Интеграция с gRPC сервисом
  - Web Dashboard

### 3. **Shift Optimizer (Microservice)**
- **Порт**: 50051 (gRPC)
- **Функции**:
  - Оптимизация расписания смен
  - Алгоритмы планирования
  - Независимый микросервис
  - Высокопроизводительные вычисления

### 4. **PostgreSQL (Database)**
- **Порт**: 5432
- **Функции**:
  - Хранение данных пользователей
  - Информация о складах и сменах
  - Данные о грузах
  - ACID транзакции

## API Endpoints

### Основные маршруты:
- `GET /` → Dashboard (главная страница)
- `GET /dashboard/` → Веб-интерфейс с графиками
- `POST /api/auth/login/` → Аутентификация
- `GET /api/shifts/` → Список смен
- `POST /api/shifts/optimize/` → Оптимизация смен
- `GET /api/warehouses/` → Управление складами
- `GET /api/cargo/` → Управление грузами

## Docker Compose Services

```yaml
services:
  nginx:          # API Gateway
  app:            # Django Application  
  shift_optimizer: # gRPC Optimization Service
  db:             # PostgreSQL Database
```

## Технологический стек

- **Backend**: Django REST Framework, Python 3.12
- **Database**: PostgreSQL 15
- **Microservice**: gRPC, Protocol Buffers
- **Frontend**: Bootstrap 5, Chart.js, Vanilla JS
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: Swagger/OpenAPI
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx (в продакшене) 