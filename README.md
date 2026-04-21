# Cart Service

> Микросервис для интернет-магазина электроники. Главный репозиторий: [microservices-shop/overview](https://github.com/microservices-shop/overview)

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.132-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.18-6BA81E?style=for-the-badge)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.12-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![FastStream](https://img.shields.io/badge/FastStream-0.6-00C7B7?style=for-the-badge)
![httpx](https://img.shields.io/badge/httpx-0.28-0096D6?style=for-the-badge)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![structlog](https://img.shields.io/badge/structlog-25.5-000000?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-24-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Описание

Микросервис управления корзинами покупателей.

Сервис отвечает за хранение и управление товарами в корзинах пользователей. Для быстрого отображения данные товаров (название, цена, изображение) сохраняются локально при добавлении. Когда в каталоге меняется цена или товар становится недоступен — сервис получает уведомление и обновляет сохранённые данные, чтобы пользователь видел актуальную информацию.

**Основной функционал:**
- **Управление корзиной** — добавление товаров с сохранением локальных копий данных, изменение количества, выбор товаров для заказа (чекбоксы), удаление позиций
- **Быстрое отображение** — корзина загружается из локальной БД без запросов к другим сервисам
- **Синхронизация данных** — автоматическое обновление локальных копий товаров через webhooks при изменении цены, если товар закончился или удалён из каталога
- **Интеграция с заказами** — предоставление выбранных товаров для Order Service, асинхронная очистка корзины после оплаты через RabbitMQ

## Структура проекта

```
cart-service/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── cart.py            # REST эндпоинты (публичный API)
│   │   │   └── router.py          
│   │   ├── internal/
│   │   │   ├── cart.py            # Internal API для Order Service
│   │   │   ├── sync.py            # Webhooks от Product Service
│   │   │   └── router.py          
│   │   └── dependencies.py        
│   ├── db/
│   │   ├── database.py            # Конфигурация БД
│   │   └── models.py              # SQLAlchemy модели
│   ├── repositories/
│   │   └── cart.py                
│   ├── services/
│   │   ├── cart.py                
│   │   └── product_client.py      
│   ├── messaging/
│   │   ├── broker.py              
│   │   ├── consumer.py            
│   │   └── schemas.py             
│   ├── middleware/
│   │   └── request_logger.py      
│   ├── schemas/                   # Pydantic схемы
│   │   ├── cart.py                
│   │   ├── product.py             
│   │   └── internal.py            
│   ├── config.py                  # Конфигурация (pydantic-settings)
│   ├── logger.py                  
│   ├── exceptions.py              
│   └── main.py                    # Точка входа приложения
├── alembic/                       # Миграции БД
├── pyproject.toml                 
├── .env.example                  
└── README.md
```

## API

Сервис запускается на порту **8003**. Интерактивная документация доступна по адресу `http://localhost:8003/docs` (Swagger UI).

### Публичный API (`/api/v1/cart`)

| Метод    | Путь                          | Описание                                                      | Заголовки   |
|----------|-------------------------------|---------------------------------------------------------------|-------------|
| `GET`    | `/api/v1/cart`                | Получить корзину со снапшотами и флагами изменений            | `X-User-Id` |
| `POST`   | `/api/v1/cart/items`          | Добавить товар в корзину (запрос снапшота у Product Service)  | `X-User-Id` |
| `PATCH`  | `/api/v1/cart/items/{id}`     | Изменить количество товара                                    | `X-User-Id` |
| `PATCH`  | `/api/v1/cart/items/{id}/select` | Изменить статус выбора товара (чекбокс)                   | `X-User-Id` |
| `PATCH`  | `/api/v1/cart/select-all`     | Выбрать/снять выбор со всех доступных товаров                 | `X-User-Id` |
| `DELETE` | `/api/v1/cart/items/{id}`     | Удалить товар из корзины                                      | `X-User-Id` |
| `DELETE` | `/api/v1/cart`                | Очистить всю корзину                                          | `X-User-Id` |

### Internal API (Order Service)

| Метод    | Путь                          | Описание                                                      |
|----------|-------------------------------|---------------------------------------------------------------|
| `GET`    | `/internal/cart/selected`     | Получить выбранные товары (для оформления заказа)            |
| `GET`    | `/internal/cart/{user_id}`    | Получить корзину пользователя                                 |
| `DELETE` | `/internal/cart/{user_id}`    | Очистить корзину пользователя                                 |

### Internal API (Product Service Webhooks)

| Метод  | Путь                                          | Описание                                    |
|--------|-----------------------------------------------|---------------------------------------------|
| `POST` | `/internal/cart/products/{id}/updated`        | Webhook: товар обновлён (цена, название)    |
| `POST` | `/internal/cart/products/{id}/out-of-stock`   | Webhook: товар закончился (stock = 0)       |
| `POST` | `/internal/cart/products/{id}/back-in-stock`  | Webhook: товар снова в наличии (stock > 0)  |
| `POST` | `/internal/cart/products/{id}/deleted`        | Webhook: товар удалён из каталога           |

### Health Check

| Метод | Путь      | Описание           |
|-------|-----------|--------------------|
| `GET` | `/health` | Проверка здоровья  |

## RabbitMQ Интеграция

### Подписки (Consumers)

| Очередь              | Обработчик                      | Описание                                    |
|----------------------|---------------------------------|---------------------------------------------|
| `cart.items.remove`  | `cart_items_remove_subscriber()`| Удаление оплаченных товаров из корзины      |

## Установка и запуск

### Требования

- Python 3.12+
- PostgreSQL 14+
- RabbitMQ 3.12+

### Разработка

```bash
# Установка зависимостей
uv sync

cp .env.example .env

# Запуск PostgreSQL
docker-compose -f docker-compose.dev.yml up -d

# Миграции БД
alembic upgrade head

# Запуск сервиса
uvicorn src.main:app --reload --port 8003 --no-access-log
```

### Production

```bash
docker-compose up --build -d
```

