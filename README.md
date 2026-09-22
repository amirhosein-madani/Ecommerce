# 🛒 E-commerce API

A modular e-commerce backend built with **Django** and **Django REST Framework**, designed around RESTful APIs, authentication, product management, shopping cart, orders, payments, reviews, customer support, caching, background tasks, and automated testing.

## ✨ Features

### 👤 Authentication & Accounts

* User registration and authentication
* JWT authentication with SimpleJWT
* Token blacklisting
* User profile management
* Password management
* Authentication and authorization

### 🛍️ Products

* Product management
* Category management
* Product publishing workflow
* Product images
* Stock management
* Discount and final price calculation
* Product filtering
* Pagination

### 🛒 Shopping Cart

* Database-backed shopping cart
* Add and remove products
* Quantity management
* Stock validation
* Cart ownership per user
* Cart item uniqueness

### 📦 Orders & Checkout

* Checkout workflow
* Order management
* Order status handling
* User addresses
* Coupon usage
* Order-related validation

### 💳 Payments

* Payment workflow
* ZarinPal sandbox integration
* Payment status handling

### ⭐ Reviews

* Product reviews
* Rating system
* Review moderation
* Customer review permissions
* Admin review management
* One review per user/product

### 💬 Customer Support

* Support ticket system
* Ticket messages
* Ticket categories
* Priority levels
* Ticket status management
* User/admin access control

### ❤️ Wishlist

* User wishlist functionality
* Product-based wishlist management

---

## ⚙️ Backend Architecture

The project is organized into separate Django applications based on domain responsibilities.

```text
apps/
├── accounts/
├── cart/
├── dashboard/
├── order/
├── payment/
├── products/
├── reviews/
└── website/
```

The architecture separates concerns between different business domains while keeping shared project configuration inside the `core` package.

---

## 🔐 Authentication & Authorization

The API uses **Django REST Framework** together with **SimpleJWT**.

Authorization is handled through DRF permissions and application-level user roles.

The project includes:

* JWT authentication
* Authentication-required endpoints
* Read-only access for unauthenticated users where appropriate
* Object-level permissions
* Admin-specific access
* Customer-specific access

---

## ⚡ Caching & Background Tasks

The project uses **Redis** for caching and **Celery** for asynchronous background task processing.

### Redis

Used as the caching layer for backend operations where caching is beneficial.

### Celery

Used for background task processing.

### Celery Beat

Included for scheduled task execution.

```text
Django
   │
   ├── Redis ────────── Cache
   │
   └── Celery ───────── Background Tasks
          │
          └── Celery Beat ─── Scheduled Tasks
```

---

## 🧪 Testing

The project uses **pytest** and **pytest-django** for automated testing.

Testing tools include:

* pytest
* pytest-django
* Faker

The test suite is used to verify API behavior, authentication, permissions, business logic, and application workflows.

---

## 📚 API Documentation

The API is documented using **drf-spectacular**.

Available documentation interfaces:

* Swagger UI
* Redoc
* OpenAPI schema

This makes it possible to inspect available endpoints, request parameters, serializers, authentication requirements, and responses.

---

## 🐳 Docker

The development environment is containerized with **Docker Compose**.

### Services

```text
┌─────────────────┐
│     Backend     │
│     Django      │
│      :8000      │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌────────┐  ┌────────┐
│Postgres│  │ Redis  │
│  :5432 │  │ :6379  │
└────────┘  └───┬────┘
                │
                ▼
           ┌─────────┐
           │ Celery  │
           │ Worker  │
           └─────────┘

┌───────────────┐
│   smtp4dev    │
│ Email Testing │
└───────────────┘
```

### Docker Services

* Django backend
* PostgreSQL 15
* Redis
* Celery worker
* smtp4dev

---

## 🧰 Tech Stack

| Category          | Technologies                    |
| ----------------- | ------------------------------- |
| Language          | Python                          |
| Framework         | Django 5.2                      |
| API               | Django REST Framework           |
| Authentication    | SimpleJWT                       |
| Database          | PostgreSQL 15                   |
| Cache             | Redis                           |
| Background Tasks  | Celery                          |
| Scheduling        | Celery Beat                     |
| API Documentation | drf-spectacular, Swagger, Redoc |
| Testing           | pytest, pytest-django, Faker    |
| Email Testing     | smtp4dev                        |
| Containerization  | Docker, Docker Compose          |
| Code Quality      | Black, Flake8                   |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/amirhosein-madani/Ecommerce.git
cd Ecommerce
```

### 2. Configure environment variables

Create the development environment file:

```text
envs/dev/.env
```

Configure the required Django, PostgreSQL, Redis, email, and payment settings.

### 3. Start the services

```bash
docker compose up --build
```

The Django development server will be available at:

```text
http://localhost:8000
```

---

## 🧪 Running Tests

Run the test suite inside the backend container:

```bash
docker compose exec backend pytest
```

---

## 📖 API Documentation

After starting the project, the Swagger and Redoc interfaces can be accessed through the configured API documentation endpoints.

---

## 🗂️ Project Structure

```text
Ecommerce/
│
├── apps/
│   ├── accounts/
│   ├── cart/
│   ├── dashboard/
│   ├── order/
│   ├── payment/
│   ├── products/
│   ├── reviews/
│   └── website/
│
├── core/
│   ├── settings/
│   ├── urls.py
│   └── ...
│
├── dockerfiles/
│   └── dev/
│
├── envs/
│   └── dev/
│
├── tests/
│
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 🎯 Project Goals

This project is built to practice and demonstrate backend development concepts including:

* REST API design
* Django application architecture
* Authentication & authorization
* Database modeling
* Business logic implementation
* API validation
* Caching
* Background task processing
* Automated testing
* API documentation
* Dockerized development

---

## 👨‍💻 Author

**Amir Madani**

Backend Developer focused on Python, Django, and Django REST Framework.

📧 [amirmadani901@gmail.com](mailto:amirmadani901@gmail.com)

💼 LinkedIn: https://www.linkedin.com/in/amir-madanii/

🐙 GitHub: https://github.com/amirhosein-madani
