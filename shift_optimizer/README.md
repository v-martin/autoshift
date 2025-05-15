# Shift Optimizer

Модуль для оптимизации распределения смен в системе AutoShift. Позволяет автоматически назначать сотрудников на смены в разных складах с учетом квалификаций сотрудников, нагрузки на склады и предпочтений сотрудников.

## Структура модуля

```
shift_optimizer/
├── protos/                  # Определения протоколов gRPC
│   ├── shift_optimizer.proto  # Основной Proto-файл
│   └── generate_grpc.py       # Скрипт для генерации Python-кода из Proto
├── server/                  # Серверная часть
│   ├── models.py              # Модели данных для оптимизатора
│   ├── optimizer.py           # Алгоритм оптимизации
│   └── server.py              # gRPC сервер
├── client/                  # Клиентская часть
│   ├── client.py              # gRPC клиент
│   └── django_integration.py  # Интеграция с Django
└── tests/                   # Тесты
    ├── test_server.py         # Тесты серверной части
    ├── test_client.py         # Тесты клиента
    └── test_django_integration.py  # Тесты Django интеграции
```

## Установка и запуск

### Зависимости

Для работы модуля необходимы следующие зависимости:

```
grpcio==1.48.0
grpcio-tools==1.48.0
protobuf==4.23.0
```

### Генерация gRPC кода

Перед первым использованием необходимо сгенерировать Python-код из Proto-файла:

```bash
cd shift_optimizer/protos
python generate_grpc.py
```

### Запуск сервера

```bash
# Простой запуск
python -m shift_optimizer.server.server

# С указанием порта (по умолчанию 50051)
python -m shift_optimizer.server.server --port=50052
```

## Использование в Django

Интеграция с Django происходит через класс `ShiftOptimizationService` из модуля `client.django_integration`:

```python
from shift_optimizer.client.django_integration import ShiftOptimizationService
from datetime import date

# Создаем экземпляр сервиса
service = ShiftOptimizationService()

# Оптимизируем смены на неделю
start_date = date(2023, 7, 1)
end_date = date(2023, 7, 7)
success, message, shifts, staffing = service.optimize_shifts(start_date, end_date)

if success:
    # Сохраняем результаты в базу данных
    service.save_optimized_shifts(shifts)
    print(f"Оптимизация успешна! Создано {len(shifts)} смен.")
    
    # Анализируем статус укомплектованности складов
    for staff_info in staffing:
        print(f"Склад: {staff_info['warehouse_name']}, "
              f"День: {staff_info['day']}, "
              f"Полностью укомплектован: {staff_info['is_fully_staffed']}")
else:
    print(f"Ошибка оптимизации: {message}")
```

## Настройка

Для настройки интеграции с Django добавьте следующие параметры в `settings.py`:

```python
# Настройки оптимизатора смен
SHIFT_OPTIMIZER_HOST = 'localhost'  # Хост сервера оптимизации
SHIFT_OPTIMIZER_PORT = '50051'      # Порт сервера оптимизации
```

## Алгоритм оптимизации

Оптимизация смен выполняется в несколько этапов:

1. Расчет требуемого количества сотрудников для каждого склада на основе данных о грузообороте
2. Минимальное комплектование складов сотрудниками (согласно минимальным требованиям)
3. Распределение дополнительных сотрудников на основе нагрузки
4. Учет предпочтений сотрудников при распределении
5. Формирование отчета о укомплектованности складов

Алгоритм учитывает квалификации сотрудников и их предпочтения по складам, что позволяет оптимизировать не только эффективность распределения, но и удовлетворенность сотрудников.

## Тестирование

Запуск тестов:

```bash
# Запуск всех тестов
python -m unittest discover -s shift_optimizer/tests

# Запуск конкретного теста
python -m unittest shift_optimizer.tests.test_server
``` 