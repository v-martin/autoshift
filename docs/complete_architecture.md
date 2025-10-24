# AutoShift - Полная архитектура системы

## Схема взаимодействия сервисов (Production Ready)

```mermaid
graph TB
    subgraph "🌐 External"
        USER[👤 Users/Clients]
        MOBILE[📱 Mobile Apps]
        API_CLIENT[🔧 API Clients]
    end
    
    subgraph "🐳 Docker Environment"
        subgraph "🚪 Gateway Layer"
            NGINX[🌐 Nginx<br/>API Gateway<br/>:80, :443<br/>Load Balancer]
        end
        
        subgraph "🏗️ Application Layer"
            DJANGO[🐍 Django API<br/>AutoShift Backend<br/>:8000<br/>REST + Dashboard]
        end
        
        subgraph "⚙️ Microservices"
            OPTIMIZER[🔧 Shift Optimizer<br/>gRPC Service<br/>:50051<br/>Optimization Engine]
        end
        
        subgraph "💾 Data Layer"
            POSTGRES[(🐘 PostgreSQL<br/>Database<br/>:5432<br/>ACID Storage)]
        end
        
        subgraph "📁 Storage"
            STATIC[📄 Static Files<br/>CSS, JS, Images]
            MEDIA[🖼️ Media Files<br/>User Uploads]
        end
    end
    
    %% External connections
    USER -->|HTTP/HTTPS| NGINX
    MOBILE -->|REST API| NGINX
    API_CLIENT -->|API Calls| NGINX
    
    %% Nginx routing
    NGINX -->|/api/*| DJANGO
    NGINX -->|/dashboard| DJANGO
    NGINX -->|/admin| DJANGO
    NGINX -->|Static Files| STATIC
    NGINX -->|Media Files| MEDIA
    
    %% Application connections
    DJANGO -->|SQL Queries<br/>CRUD Operations| POSTGRES
    DJANGO -->|gRPC Calls<br/>Optimization Requests| OPTIMIZER
    DJANGO -->|Serve Files| STATIC
    DJANGO -->|Handle Uploads| MEDIA
    
    %% Microservice connections
    OPTIMIZER -->|Read Shift Data<br/>Optimization Logic| POSTGRES
    
    %% Styling
    classDef external fill:#ff5722,stroke:#d84315,stroke-width:2px,color:#fff
    classDef gateway fill:#ff9800,stroke:#f57c00,stroke-width:3px,color:#fff
    classDef application fill:#2196f3,stroke:#1976d2,stroke-width:3px,color:#fff
    classDef microservice fill:#4caf50,stroke:#388e3c,stroke-width:3px,color:#fff
    classDef database fill:#9c27b0,stroke:#7b1fa2,stroke-width:3px,color:#fff
    classDef storage fill:#607d8b,stroke:#455a64,stroke-width:2px,color:#fff
    
    class USER,MOBILE,API_CLIENT external
    class NGINX gateway
    class DJANGO application
    class OPTIMIZER microservice
    class POSTGRES database
    class STATIC,MEDIA storage
```

## 🏗️ Архитектурные компоненты

### 1. **🌐 Nginx (API Gateway & Load Balancer)**
```
Порт: 80, 443
Функции:
├── Reverse Proxy для Django
├── SSL Termination (HTTPS)
├── Static Files Serving
├── Load Balancing
├── Rate Limiting
├── CORS Headers
└── Health Checks
```

### 2. **🐍 Django Application (Backend API)**
```
Порт: 8000 (internal)
Функции:
├── REST API Endpoints
├── JWT Authentication
├── Business Logic
├── gRPC Client Integration
├── Web Dashboard
├── Admin Interface
└── Database ORM
```

### 3. **⚙️ Shift Optimizer (gRPC Microservice)**
```
Порт: 50051
Функции:
├── Shift Optimization Algorithms
├── High-Performance Computing
├── Independent Scaling
├── Protocol Buffers
└── Async Processing
```

### 4. **🐘 PostgreSQL (Database)**
```
Порт: 5432
Функции:
├── User Management
├── Shift Scheduling Data
├── Warehouse Information
├── Cargo Management
├── ACID Transactions
└── Data Integrity
```

## 🔄 Потоки данных

### **HTTP Request Flow:**
1. **Client** → `HTTP/HTTPS` → **Nginx**
2. **Nginx** → `Proxy Pass` → **Django**
3. **Django** → `SQL` → **PostgreSQL**
4. **Django** → `gRPC` → **Shift Optimizer**
5. **Response** ← `JSON/HTML` ← **Client**

### **Optimization Flow:**
1. **User** → `POST /api/shifts/optimize/`
2. **Django** → `gRPC Call` → **Optimizer**
3. **Optimizer** → `Read Data` → **PostgreSQL**
4. **Optimizer** → `Algorithm` → **Optimized Schedule**
5. **Django** → `Update DB` → **PostgreSQL**

## 🐳 Docker Services

```yaml
services:
  nginx:           # API Gateway & Load Balancer
  app:             # Django Application
  shift_optimizer: # gRPC Optimization Service  
  db:              # PostgreSQL Database
```

## 📊 Технологический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Gateway** | Nginx | Alpine |
| **Backend** | Django REST Framework | 5.1 |
| **Language** | Python | 3.12 |
| **Database** | PostgreSQL | 15 |
| **Microservice** | gRPC + Protocol Buffers | Latest |
| **Frontend** | Bootstrap + Chart.js | 5.3 |
| **Auth** | JWT (Simple JWT) | Latest |
| **Containerization** | Docker + Docker Compose | Latest |
| **API Docs** | Swagger/OpenAPI | 3.0 |

## 🚀 Преимущества архитектуры

### **Масштабируемость**
- Независимое масштабирование сервисов
- Горизонтальное масштабирование через Nginx
- Микросервисная архитектура

### **Надежность**
- Health checks для всех сервисов
- Graceful degradation
- Database connection pooling

### **Производительность**
- Nginx кэширование статических файлов
- gRPC для высокопроизводительных вычислений
- Database indexing и оптимизация

### **Безопасность**
- JWT аутентификация
- HTTPS через Nginx
- CORS политики
- SQL injection protection 