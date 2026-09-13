# Architecture Overview

## Project Structure

The project follows a modular Django structure in which domain-specific
code is organized inside the `apps/` directory. Project-level configuration
lives separately in `core/`, and the development environment is managed
with Docker Compose.

### Directory Layout

```text
project-root/
│
├── apps/
│   ├── accounts/       # Authentication & user management
│   ├── products/       # Product catalog & categories
│   ├── cart/           # Shopping cart management
│   ├── reviews/        # Product reviews
│   ├── payment/        # Payment gateway integration
│   ├── order/          # Order creation & management
│   └── website/        # Cross-cutting, non-domain pages
│
├── core/
│   ├── settings/       # Django settings (base/dev/prod)
│   ├── urls.py         # Root URL configuration
│   └── wsgi.py / asgi.py
│
├── dockerfiles/
│   └── dev/
│       └── Dockerfile
│
├── docker-compose.yml
└── .env.example
```

## Applications

All Django applications live inside `apps/`. Each app owns its own models,
serializers/views, and business logic for its domain.

| App | Responsibility | Depends on |
|---|---|---|
| `accounts` | Authentication, registration, user profiles | — |
| `products` | Product catalog, categories | — |
| `cart` | Shopping cart & cart items | `accounts`, `products` |
| `reviews` | Product reviews & ratings | `accounts`, `products` |
| `order` | Order creation, order lifecycle | `cart`, `accounts` |
| `payment` | Payment gateway communication | `order` |
| `website` | Non-domain pages (home, static pages) | — |



## Core Configuration

The `core/` directory contains project-level Django configuration, kept
separate from domain logic:

- Django settings (split by environment, if applicable)
- Root URL configuration
- WSGI / ASGI entry points
- Any project-wide middleware or context processors

## Service Dependencies

| Service | Purpose | Defined in |
|---|---|---|
| PostgreSQL | Primary database | `docker-compose.yml` |
| Redis | Cart storage / cache | `docker-compose.yml` |
| Celery | Async tasks (emails, cleanup) | `docker-compose.yml` |


## Request Flow (Example: Checkout)

```text
Client
  │
  ▼
website / API endpoint
  │
  ▼
cart  ──►  order  ──►  payment  ──►  Payment Gateway
  │           │
  ▼           ▼
Redis     PostgreSQL
```


## Docker

The development Dockerfile is located at:

```text
dockerfiles/dev/Dockerfile
```

Docker Compose orchestrates all required services (app, database, Redis,
Celery worker, etc.).

**Start the development environment:**
```bash
docker compose up
```

**Rebuild images after dependency changes:**
```bash
docker compose up --build
```

**Environment variables:**
Copy `.env.example` to `.env` and adjust values before starting the
containers.