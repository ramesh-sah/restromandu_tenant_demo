# 🍽️ RestroMandu SaaS — Multi-Tenant Restaurant Management System

A high-performance, production-ready multi-tenant SaaS application built with **Django 6** and **django-tenants** using PostgreSQL schema-per-tenant isolation and template schema cloning for near-instant tenant provisioning.

---

## 🌟 Key Features

- **🔒 Hard Tenant Isolation:** Each restaurant gets its own PostgreSQL schema (tables: auth, products, orders, profiles). Zero cross-tenant data leak risk.
- **⚡ Fast Tenant Onboarding (< 5s):** Uses `CloneSchema` to clone structure from a pre-migrated `_template` reference schema instead of running heavy migrations for every new sign-up.
- **📊 1 GB Storage Quota Monitoring:** Tracks PostgreSQL disk usage per tenant schema in real-time with single-query aggregation and progress bar alerts.
- **🔑 Centralized Public Control Plane:** Landing page for restaurant sign-ups + global public admin panel at `/admin/` to manage tenants and domain routing.
- **🌐 Domain & Subdomain Routing:** Subdomain resolution (`restaurant.localhost:8000` or `restaurant.yourdomain.com`) + custom domain CNAME support via `Domain` model.

---

## 🏗️ Architecture Overview

```
                          ┌───────────────────────────┐
                          │   Public Control Plane    │
                          │   (schema: 'public')      │
                          │ - Landing Page & Signup   │
                          │ - Tenant & Domain Admin   │
                          └─────────────┬─────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
    ┌───────────────────────────┐                 ┌───────────────────────────┐
    │     Reference Schema      │                 │       Tenant Schema       │
    │    (schema: '_template')  │ ──(Clone NODATA)──► (schema: 'burgerpalace')│
    │ - Pre-migrated tables     │                 │ - Isolated auth_user      │
    │ - Source for fast clones  │                 │ - Isolated products       │
    └───────────────────────────┘                 │ - Isolated orders         │
                                                  └───────────────────────────┘
```

---

## 🚀 Quick Start (Development)

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ (with superuser or schema creation permissions)

### 2. Environment Setup
Create a `.env` file in the project root:
```ini
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.localhost
POSTGRES_DB=tenants
POSTGRES_USER=tenants
POSTGRES_PASSWORD=tenants
POSTGRES_HOST=109.199.124.68
POSTGRES_PORT=5467
```

### 3. Installation & Database Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations for shared (public) schema
python manage.py migrate_schemas --shared

# Create reference template schema for fast cloning
python manage.py ensure_template_schema
```

### 4. Create Public Superuser & Public Domain
```bash
python manage.py shell -c "
from tenants.models import Client, Domain
from django.contrib.auth.models import User

# Ensure public tenant & domain exist
p, _ = Client.objects.get_or_create(schema_name='public', defaults={'name': 'Public'})
Domain.objects.get_or_create(domain='localhost', tenant=p, defaults={'is_primary': True})

# Create public admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Created public admin: admin / admin123')
"
```

### 5. Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```
- **Landing Page & Signup:** `http://localhost:8000/`
- **Public Admin Panel:** `http://localhost:8000/admin/` (`admin` / `admin123`)

---

## 🛠️ Management Commands

| Command | Description |
|---|---|
| `python manage.py migrate_schemas --shared` | Run migrations on public schema |
| `python manage.py ensure_template_schema` | Create/migrate the `_template` reference schema (run after creating new migrations) |
| `python manage.py create_demo_tenants` | Create demo tenant accounts for testing |

---

## 📁 Project Structure

```
restromandu_tenant_demo/
├── config/                  # Project configuration
│   ├── settings.py          # Dual SHARED_APPS & TENANT_APPS config
│   ├── urls_public.py       # Public landing & control plane routes
│   └── urls.py              # Tenant-level app routes
├── tenants/                 # Shared tenant management app
│   ├── models.py            # Client (Tenant) & Domain models + Quota metrics
│   ├── views.py             # Public landing page & fast schema clone view
│   ├── forms.py             # Restaurant sign-up & validation form
│   └── management/commands/ # Custom commands (ensure_template_schema)
├── accounts/                # Tenant-level user accounts & dashboard
├── products/                # Tenant-level restaurant menu products
├── orders/                  # Tenant-level orders management
├── templates/               # HTML templates
│   ├── tenants/public_home.html  # Landing page with storage metrics
│   └── accounts/dashboard.html   # Tenant dashboard with storage progress bar
├── requirements.txt         # Dependencies (Django 6, django-tenants, psycopg3)
└── .env.example             # Environment variables template
```

---

## 🚢 Production Deployment Guide

### 1. Web Server & Reverse Proxy Setup (Nginx)
Configure Nginx with wildcard server name support:

```nginx
server {
    server_name .restromandu.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Wildcard SSL Certificate (Certbot)
```bash
sudo certbot certonly --manual --preferred-challenges dns -d "*.restromandu.com" -d "restromandu.com"
```

### 3. Production `.env` Settings
```ini
DEBUG=False
SECRET_KEY=your-secure-random-secret-key-here
ALLOWED_HOSTS=.restromandu.com,localhost,127.0.0.1
POSTGRES_DB=restromandu_prod
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

### 4. Database Optimization for High Scale
- **PgBouncer:** Use PgBouncer in `transaction` mode for pooling connections across hundreds of tenant schemas.
- **Background Tasks:** For high signup volume, offload `CloneSchema` execution to Celery/Django-Q workers.

---

## 📊 Storage Quota Specifications

- Default Quota: **1 GB** (1,073,741,824 bytes) per tenant schema.
- Calculation Method: PostgreSQL `pg_total_relation_size` across schema tables.
- Aggregation: Single SQL query fetches disk usage for all schemas efficiently.
- Alerting: UI progress bar changes color (`green` -> `yellow` at 80% -> `red` when exceeded).
