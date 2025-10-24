# Архитектура AutoShift - Слайд для презентации

## Схема взаимодействия сервисов

```mermaid
graph LR
    subgraph "🐳 Docker Environment"
        subgraph "Gateway"
            N[🌐 Nginx<br/>:80/443]
        end
        
        subgraph "Backend"
            D[🐍 Django API<br/>:8000]
        end
        
        subgraph "Services"
            O[⚙️ Shift Optimizer<br/>gRPC :50051]
        end
        
        subgraph "Database"
            P[(🐘 PostgreSQL<br/>:5432)]
        end
    end
    
    U[👤 Users] -->|HTTP/HTTPS| N
    N -->|Proxy| D
    D -->|gRPC| O
    D -->|SQL| P
    O -.->|Read| P
    
    classDef gateway fill:#ff9800,stroke:#e65100,stroke-width:3px,color:#fff
    classDef backend fill:#2196f3,stroke:#0d47a1,stroke-width:3px,color:#fff
    classDef service fill:#4caf50,stroke:#1b5e20,stroke-width:3px,color:#fff
    classDef database fill:#9c27b0,stroke:#4a148c,stroke-width:3px,color:#fff
    classDef user fill:#607d8b,stroke:#263238,stroke-width:3px,color:#fff
    
    class N gateway
    class D backend
    class O service
    class P database
    class U user
```

## Ключевые особенности архитектуры

### 🏗️ **Микросервисная архитектура**
- **API Gateway** (Nginx) - единая точка входа
- **Backend API** (Django) - основная бизнес-логика
- **Optimization Service** (gRPC) - независимый сервис оптимизации
- **Database** (PostgreSQL) - централизованное хранение данных

### 🐳 **Контейнеризация**
- Все сервисы изолированы в Docker контейнерах
- Простое развертывание через Docker Compose
- Масштабируемость и портируемость

### 🔄 **Взаимодействие сервисов**
- **HTTP/REST** - клиент-серверное взаимодействие
- **gRPC** - высокопроизводительная связь между сервисами
- **SQL** - работа с базой данных

### 📊 **Технологии**
- **Python 3.12** + Django REST Framework
- **gRPC** + Protocol Buffers
- **PostgreSQL 15**
- **Docker** + Docker Compose
- **Bootstrap 5** + Chart.js 