# Logistics & Shipment Tracking API Platform

A production-style REST API platform for managing the complete logistics and shipment lifecycle — from order creation and shipment processing to carrier tracking, warehouse operations, delivery, proof of delivery, notifications, and audit logging.

Built with **FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, Alembic, Pytest, and Docker**.

---

## 📌 Project Overview

The Logistics & Shipment Tracking API Platform is designed to simulate a real-world logistics backend used by businesses to manage orders, shipments, carriers, warehouses, delivery agents, tracking events, delivery attempts, exceptions, notifications, and operational reporting.

The platform provides secure REST APIs with:

* JWT authentication
* Role-based access control
* Shipment lifecycle management
* Real-time tracking events
* Carrier management
* Warehouse management
* Delivery management
* Proof of delivery
* Shipment exceptions
* Notifications
* Webhook processing
* Audit logging
* Reporting
* Redis-based rate limiting
* Celery background processing
* Automated testing
* Dockerized development environment

---

## 🚀 Key Features

### 🔐 Authentication & Authorization

* JWT-based authentication
* Secure password hashing using Argon2
* Role-based access control
* Protected API endpoints
* Active/inactive user validation
* API client authentication

### 👥 User & Role Management

Supported roles:

* Super Admin
* Operations Manager
* Warehouse Staff
* Delivery Agent
* Customer
* API Client

Each role has controlled access to platform resources based on permissions.

---

## 📦 Order Management

The platform supports:

* Order creation
* Order item management
* Order retrieval
* Order updates
* Order status management
* Order lifecycle validation

Invalid order status transitions are rejected by the API.

---

## 🚚 Shipment Management

Shipment management is one of the core modules of the platform.

Supported shipment lifecycle:

```text
CREATED
   ↓
CONFIRMED
   ↓
PICKUP_SCHEDULED
   ↓
PICKED_UP
   ↓
AT_ORIGIN_WAREHOUSE
   ↓
IN_TRANSIT
   ↓
AT_DESTINATION_WAREHOUSE
   ↓
OUT_FOR_DELIVERY
   ↓
DELIVERED
```

Alternative shipment states include:

```text
CANCELLED
ON_HOLD
DELIVERY_FAILED
RETURN_INITIATED
RETURNED
LOST
DAMAGED
```

The API validates shipment state transitions to prevent invalid workflow changes.

---

## 📍 Shipment Tracking

Tracking events provide a complete shipment timeline.

Each tracking event can contain:

* Shipment
* Status
* Location
* Facility
* Description
* Event time
* Created by
* Event source

Supported event sources include:

* SYSTEM
* WAREHOUSE
* DELIVERY_AGENT
* CARRIER_API
* CUSTOMER_SERVICE

Shipment status changes automatically generate tracking events where applicable.

---

## 🏢 Carrier Management

The platform supports carrier management with an adapter-based architecture.

The carrier integration layer is designed around a common service interface:

```text
CarrierService
      │
      ├── DHLAdapter
      ├── FedExAdapter
      ├── DelhiveryAdapter
      └── CustomCarrierAdapter
```

Supported carrier operations are designed for:

* Create shipment
* Get tracking information
* Cancel shipment
* Generate shipping label

This architecture allows additional carriers to be integrated without changing the core shipment workflow.

---

## 🏭 Warehouse Management

Warehouse functionality includes:

* Warehouse creation
* Warehouse management
* Origin warehouse assignment
* Destination warehouse assignment
* Shipment movement through warehouse stages

---

## 👤 Delivery Agent Management

The platform supports dedicated delivery-agent workflows.

Features include:

* Delivery agent management
* Agent profile
* Shipment assignment
* Active assignment validation
* Delivery attempt processing

---

## 🚪 Delivery Management

The delivery workflow supports:

### Delivery Attempts

Each shipment can have multiple delivery attempts.

Supported attempt statuses:

```text
SUCCESS
FAILED
RESCHEDULED
```

Failed delivery attempts require a failure reason.

Successful delivery attempts can be associated with proof of delivery.

### Proof of Delivery

The platform supports proof-of-delivery records for successfully delivered shipments.

---

## ⚠️ Shipment Exceptions

Shipment exceptions can be created for operational problems such as:

```text
DAMAGED
LOST
ADDRESS_ISSUE
CUSTOMER_UNAVAILABLE
WEATHER_DELAY
OTHER
```

Exception statuses:

```text
OPEN
RESOLVED
```

Resolution notes are required when resolving an exception.

---

## 🔔 Notifications

The platform includes shipment notification automation.

Notification lifecycle:

```text
PENDING → SENT → READ
```

Notifications can be associated with shipment events and processed through background workers.

Supported notification concepts include:

* Shipment status notifications
* Delivery notifications
* Exception notifications
* Webhook-triggered notifications

---

## 🔗 Webhook Processing

The platform supports carrier webhook processing.

Webhook workflow:

```text
Carrier Webhook
      ↓
Validate Webhook
      ↓
Find Shipment
      ↓
Create Tracking Event
      ↓
Update Shipment Status
      ↓
Create Audit Log
      ↓
Trigger Notification
```

This allows external carrier systems to update shipment information through the API.

---

## 📊 Reporting

Reporting APIs provide operational insights including:

* Shipment summary
* Delivery performance
* Carrier performance
* Shipment exceptions

These reports can be used by operations teams to monitor logistics activity.

---

## 📝 Audit Logging

Important system operations are recorded using audit logs.

Audit information can include:

* User
* Action
* Entity
* Entity ID
* Previous value
* New value
* IP address
* Timestamp

This provides traceability for important business operations.

---

## ⚡ Redis Rate Limiting

Redis is used for API rate limiting.

The rate limiter uses atomic Redis operations to track requests within a configured time window.

Example configuration:

```env
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

When the request limit is exceeded, the API returns:

```text
429 Too Many Requests
```

---

## 🔄 Background Processing with Celery

Celery is used for background processing.

Example workflow:

```text
API Request
     ↓
Create Notification
     ↓
Queue Background Task
     ↓
Celery Worker
     ↓
Notification Dispatch
```

Redis is used as the Celery broker/backend.

---

## 🧪 Automated Testing

The project includes automated API tests using:

* Pytest
* HTTPX
* FastAPI TestClient

The test suite covers major application modules including:

* Health
* Authentication
* Users
* Customers
* Addresses
* Orders
* Shipments
* Tracking events
* Carriers
* Warehouses
* Delivery agents
* Shipment assignments
* Delivery attempts
* Proof of delivery
* Shipment exceptions
* Notifications
* Webhooks
* Reports
* API clients
* End-to-end shipment workflow

Tests can also be executed inside Docker using the dedicated test runner.

```bash
docker compose run --rm test_runner
```

---

# 🐳 Docker Architecture

The project provides a Docker Compose environment containing:

```text
                    ┌─────────────────────┐
                    │      FastAPI API     │
                    │      Port: 8000      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ PostgreSQL  │   │    Redis    │   │   Celery    │
      │             │   │             │   │   Worker    │
      └─────────────┘   └─────────────┘   └─────────────┘
                               │
                               ▼
                       Background Tasks
```

Docker services:

```text
postgres
redis
api
celery_worker
test_runner
```

---

# 🛠 Technology Stack

| Technology        | Purpose                      |
| ----------------- | ---------------------------- |
| Python            | Backend programming language |
| FastAPI           | REST API framework           |
| PostgreSQL        | Relational database          |
| SQLAlchemy        | ORM                          |
| Alembic           | Database migrations          |
| Pydantic          | Data validation              |
| JWT               | Authentication               |
| Argon2            | Password hashing             |
| Redis             | Rate limiting & task broker  |
| Celery            | Background processing        |
| Pytest            | Automated testing            |
| HTTPX             | API testing                  |
| Docker            | Containerization             |
| Docker Compose    | Multi-container environment  |
| OpenAPI / Swagger | API documentation            |
| Git               | Version control              |
| GitHub            | Source code hosting          |

---

# 📁 Project Structure

```text
Logistics-Shipment-Tracking-API/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── roles.py
│   │   └── celery_app.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── integrations/
│   ├── workers/
│   ├── middleware/
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_orders.py
│   ├── test_shipments.py
│   ├── test_tracking_events.py
│   ├── test_delivery_attempts.py
│   ├── test_proof_of_delivery.py
│   ├── test_notifications.py
│   ├── test_webhooks.py
│   ├── test_reports.py
│   ├── test_api_clients.py
│   └── test_end_to_end_workflow.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# ⚙️ Local Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Logistics-Shipment-Tracking-API
```

## 2. Create virtual environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scripts\activate
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
APP_NAME=Logistics & Shipment Tracking API
APP_VERSION=1.0.0

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/logistics_db

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0

RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

> Never commit `.env` files or production secrets to GitHub.

---

# 🗄️ Database Migration

Run:

```powershell
alembic upgrade head
```

---

# ▶️ Run the API

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📚 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 🐳 Running with Docker

Build the containers:

```powershell
docker compose build
```

Start the application:

```powershell
docker compose up -d
```

Check running services:

```powershell
docker compose ps
```

View API logs:

```powershell
docker compose logs --tail=50 api
```

View Celery logs:

```powershell
docker compose logs --tail=50 celery_worker
```

Run automated tests:

```powershell
docker compose run --rm test_runner
```

Stop the environment:

```powershell
docker compose down
```

---

# 📸 Screenshots

The following screenshots demonstrate the major parts of the platform.

## Swagger API Documentation

<img width="1905" height="999" alt="swagger-overview" src="https://github.com/user-attachments/assets/cee8954b-a0a6-4616-8514-33fcab9cc0ec" />

<img width="1895" height="992" alt="swagger-overview-2" src="https://github.com/user-attachments/assets/3456f12d-5cbe-41e1-9c91-ec4e8c5e103d" />

<img width="1904" height="995" alt="swagger-overview-3" src="https://github.com/user-attachments/assets/9b4fa44d-8fa8-4d10-86a7-b0e62a194caf" />

<img width="1882" height="990" alt="swagger-overview-4" src="https://github.com/user-attachments/assets/b9cc34b7-0947-4515-bf12-2577a0cb94b6" />

<img width="1912" height="984" alt="swagger-overview-5" src="https://github.com/user-attachments/assets/ac3d9865-4127-4ea3-864c-3472cd3014b6" />

<img width="1893" height="990" alt="swagger-overview-6" src="https://github.com/user-attachments/assets/d5c7a3c1-31e2-4808-a1aa-a16f410759dd" />

<img width="1889" height="990" alt="swagger-overview-7" src="https://github.com/user-attachments/assets/dd12af58-5f5d-4983-9d2d-3550fa0d9550" />

<img width="1897" height="1000" alt="swagger-overview-8" src="https://github.com/user-attachments/assets/83c76d6a-0636-414c-b1a5-ce6ab802d264" />

<img width="1903" height="992" alt="swagger-overview-9" src="https://github.com/user-attachments/assets/78e3122b-d9c0-4f10-b51f-445e7d5d6fa4" />

<img width="1911" height="979" alt="swagger-overview-10" src="https://github.com/user-attachments/assets/9fe4c1ac-85e7-48b1-bd47-ca58eba0356a" />

<img width="1899" height="998" alt="swagger-overview-11" src="https://github.com/user-attachments/assets/081560a9-ab09-42c0-a554-81284f61f970" />


## Authentication

<img width="784" height="811" alt="swagger-authentication" src="https://github.com/user-attachments/assets/646f6494-be06-4414-811b-00118b2bbbb7" />

<img width="1859" height="950" alt="Screenshot 2026-10-03 110749" src="https://github.com/user-attachments/assets/1d0e62c3-4408-428b-8096-80f942b0896d" />


## Shipment Management

#creating
<img width="716" height="858" alt="image" src="https://github.com/user-attachments/assets/7d4b444e-d1ef-4d14-9d11-4c12b8e0840e" />

## Shipment Tracking

<img width="941" height="936" alt="image" src="https://github.com/user-attachments/assets/db9c7458-8cf1-44a7-88b9-f390cc5d0a6d" />

## Delivery Workflow

<img width="964" height="949" alt="image" src="https://github.com/user-attachments/assets/e4aea9d2-16da-4a5b-8691-f70698abd67e" />

## Webhook Processing

<img width="734" height="877" alt="image" src="https://github.com/user-attachments/assets/a70945ef-0bf8-485a-9586-e20fa6d42706" />


## Reporting

<img width="1307" height="930" alt="image" src="https://github.com/user-attachments/assets/49552ad1-6130-469e-b663-36d107f6d25e" />

<img width="1457" height="875" alt="image" src="https://github.com/user-attachments/assets/e80620cc-cc2e-4288-a152-67c555a89752" />

<img width="1336" height="835" alt="image" src="https://github.com/user-attachments/assets/6ab2769f-ceb3-4838-8e2e-87b78ae533d0" />

<img width="1313" height="846" alt="image" src="https://github.com/user-attachments/assets/2ba461e3-02cc-40bd-b359-a3d569b043c8" />

## Automated Tests

<img width="1920" height="1022" alt="automated-test" src="https://github.com/user-attachments/assets/90c9fa6e-4840-4259-932c-c0fe9f421a4a" />

<img width="1920" height="1018" alt="docker-automated-test" src="https://github.com/user-attachments/assets/03804f9e-d2b3-4023-8ed6-929a10143dd1" />

## Docker Containers

<img width="1920" height="991" alt="docker-platform" src="https://github.com/user-attachments/assets/32eb7941-d516-4a96-9f05-f54bbc98f640" />


> Add or remove screenshots depending on which parts of the application you want to highlight.

---

# 🔄 End-to-End Shipment Workflow

A complete shipment workflow can be represented as:

```text
Customer
   │
   ▼
Create Order
   │
   ▼
Confirm Order
   │
   ▼
Create Shipment
   │
   ▼
Assign Carrier
   │
   ▼
Schedule Pickup
   │
   ▼
Pickup
   │
   ▼
Origin Warehouse
   │
   ▼
In Transit
   │
   ▼
Destination Warehouse
   │
   ▼
Out for Delivery
   │
   ▼
Delivery Attempt
   │
   ├── Failed ──→ Reschedule / Exception
   │
   └── Success
          │
          ▼
   Proof of Delivery
          │
          ▼
       Delivered
          │
          ▼
    Notification
          │
          ▼
      Audit Log
```

---

# 🔐 Security Features

The project includes several security measures:

* JWT authentication
* Argon2 password hashing
* Role-based authorization
* Inactive user protection
* API client authentication
* Redis-based rate limiting
* Request body size protection
* Configurable CORS
* Security response headers
* Generic internal server error responses
* Webhook validation
* Audit logging

---

# 🎯 Project Goals

This project was developed to demonstrate practical backend engineering skills including:

* REST API development
* Backend architecture
* Database design
* Authentication and authorization
* Business workflow implementation
* State-machine based status management
* Third-party integration architecture
* Background processing
* Redis usage
* Automated testing
* Docker containerization
* API security
* Auditability
* Production-style project organization

---

# 🔮 Future Enhancements

Potential future improvements include:

* Real carrier API integrations
* Email/SMS provider integrations
* Push notifications
* Advanced analytics dashboards
* Object storage for proof-of-delivery files
* CI/CD pipeline
* Kubernetes deployment
* API gateway integration
* Advanced observability and monitoring

---

# 👨‍💻 Author

**Ramakrushna**

Backend / Full-Stack Web Developer

### Skills demonstrated in this project

```text
Python
FastAPI
PostgreSQL
SQLAlchemy
Alembic
Redis
Celery
JWT
Pytest
Docker
REST APIs
RBAC
API Security
Background Processing
Database Design
```

---

