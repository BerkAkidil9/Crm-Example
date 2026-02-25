# Darkenyas CRM

**Live demo:** [https://darkenyas-crm.onrender.com/](https://darkenyas-crm.onrender.com/)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

A multi-tenant Django CRM with role-based access for organisations and agents.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Local Setup](#local-setup)
- [Email Configuration](#email-configuration)
- [Deploy on Render](#deploy-on-render)
- [Project Structure](#project-structure)
- [Management Commands](#management-commands)
- [Testing](#testing)

---

## Tech Stack

**Backend:** Django 5.0 · Python 3.12 · Crispy Forms · django-phonenumber-field · python-dotenv

**Frontend:** Tailwind CSS · Chart.js · Flatpickr

**Database:** PostgreSQL (development & production)

**Email:** Gmail API (Render) or SMTP (local) — signup verification, password reset

---

## Features

### Roles

| Role | Access |
|------|--------|
| **Administrator** | Full system: all organisors, agents, leads, products, orders, finance, tasks, notifications, activity log |
| **Organisor** | Own organisation: profile, agents, leads, products, orders, finance, tasks, notifications, activity within org |
| **Agent** | Assigned leads, own orders, products (view only), personal tasks, notifications, activity affecting them |

### Modules

| Module | Features |
|--------|----------|
| **Leads** | CRUD, agent assignment; source & value categories; personal info (first name, last name, age, email, address, phone, profile photo); activity history; org/agent filters |
| **Agents** | CRUD, personal info (first name, last name, email, username, phone, date of birth, gender, profile photo); list by organisation |
| **Organisors** | Organisation CRUD; Admin manages all, Organisor manages own profile |
| **Products & Stock** | Category/subcategory; stock levels, minimum threshold; discounts (%, fixed, date range); bulk price update; sales dashboard; charts; stock movements; price history; stock alerts (low/out/overstock); stock recommendations |
| **Orders** | Orders linked to leads; product line items; auto stock reduce on order; stock restore on cancel; org/agent filters |
| **Finance** | Date range reports; filter by order creation date or order delivery date; org/agent filters; earnings, cost, profit |
| **Tasks** | Status, priority; assign to agents; org/agent filters; notifications — **Organisor:** order created, sale completed today, stock alert; **Agent:** task assigned, lead assigned, order created (for their leads), sale completed today, deadline reminders (1 or 3 days before), lead no order in 30 days |
| **Activity Log** | Audit trail for leads, orders, tasks, agents, organisors, products; org/agent filters |

### Authentication

Signup · Email verification · Login (email or username) · Password reset · Profile photo · Phone number

---

## Local Setup

**Prerequisites:** Python 3.12+

### 1. Clone and enter project

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git clone https://github.com/YOUR_USERNAME/Crm-Example.git
cd Crm-Example
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Copy the example file and edit it:

- **Windows:** `copy .env.example .env`
- **Mac/Linux:** `cp .env.example .env`

For local development:

- `SECRET_KEY` — generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DEBUG=True` — leave as is for development
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` — PostgreSQL credentials (create DB: `createdb djcrm`)

For signup & password reset: either SMTP (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) or Gmail API (`USE_GMAIL_API=true` + Gmail API vars) — see [Email Configuration](#email-configuration).

For persistent profile/media uploads in production (e.g. Render), see [docs/CLOUDFLARE_R2.md](docs/CLOUDFLARE_R2.md) (Cloudflare R2 setup).

The app uses **PostgreSQL** by default (matches production).

### 5. Database and run

Create the PostgreSQL database (if not exists), then migrate:

```bash
createdb djcrm   # or create via pgAdmin
python manage.py migrate
python manage.py createsuperuser   # Create admin (email, username, password)
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and log in with your superuser credentials.

### Local SQLite (optional)

To use SQLite instead of PostgreSQL, comment out `DB_ENGINE` and `DB_*` in `.env`. The app will fall back to SQLite.

---

## Email Configuration

For signup verification and password reset you can use either option.

**Option A – Local (SMTP)**  
1. Enable **2-Step Verification** in your Gmail account  
2. Create an **App Password**: Google Account → Security → App passwords → Mail → Other  
3. In `.env`: set `USE_GMAIL_API=false` (or leave unset) and add `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

**Option B – Gmail API (needed on Render; SMTP ports are blocked)**  
For step-by-step setup (Google Cloud project, Gmail API, OAuth consent screen, OAuth 2.0 Client ID, refresh token), see **[docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)**.  
Then in `.env`: set `USE_GMAIL_API=true` and add `GMAIL_API_CLIENT_ID`, `GMAIL_API_CLIENT_SECRET`, `GMAIL_API_REFRESH_TOKEN`, `DEFAULT_FROM_EMAIL` (the Gmail address used for the refresh token).

---

## Deploy on Render

The project uses Gunicorn and WhiteNoise. Deploy via the included `render.yaml` Blueprint.

### 1. Create a PostgreSQL database

Use [Neon](https://neon.tech/) (recommended) or any PostgreSQL provider. Copy the **pooled connection string** (Neon: Connection Details → Pooled connection).

### 2. Create a new Web Service on Render

1. Connect your GitHub repo
2. Render will detect `render.yaml` — use **Apply** to create the service
3. In **Environment** → **Environment Variables**, add the variables below

### 3. Environment variables (Render Dashboard)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string (e.g. Neon pooled URL with `?sslmode=require`) |
| `SECRET_KEY` | ✅ Yes | Random string (Render can auto-generate) |
| `DEBUG` | ✅ Yes | Set to `False` for production |
| `GMAIL_API_CLIENT_ID` | ✅ Yes | From Google Cloud Console (OAuth 2.0 Client ID). See [docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md) |
| `GMAIL_API_CLIENT_SECRET` | ✅ Yes | From Google Cloud Console. See [docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md) |
| `GMAIL_API_REFRESH_TOKEN` | ✅ Yes | From `gmail_oauth2 --generate_oauth2_token`. See [docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md) |
| `DEFAULT_FROM_EMAIL` | ✅ Yes | Gmail address that sends mail (same as the account used for the refresh token) |
| `DJANGO_SUPERUSER_EMAIL` | Optional | Email for first admin (created on first deploy) |
| `DJANGO_SUPERUSER_USERNAME` | Optional | Username for first admin |
| `DJANGO_SUPERUSER_PASSWORD` | Optional | Password for first admin |
| R2 (media) | Optional | For persistent uploads: `USE_R2`, `R2_ACCOUNT_ID`, `R2_BUCKET_NAME`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_PUBLIC_DOMAIN`. See [docs/CLOUDFLARE_R2.md](docs/CLOUDFLARE_R2.md) |

`USE_GMAIL_API`, `PYTHON_VERSION`, `WEB_CONCURRENCY`, and `RENDER_EXTERNAL_HOSTNAME` are set automatically by `render.yaml` or Render.

### 4. Deploy

After saving env vars, Render will build and deploy. The first deploy runs migrations and creates a superuser if `DJANGO_SUPERUSER_*` vars are set.

---

## Project Structure

```
├── agents/            # Agent CRUD, profile
├── organisors/        # Organisor (organisation) management
├── djcrm/             # Main project (settings, urls)
├── finance/           # Financial reports (date range, org/agent filters)
├── leads/             # Lead management, auth, categories
├── orders/            # Order management (products, leads)
├── ProductsAndStock/  # Products, stock, dashboard, charts, alerts
├── tasks/             # Tasks and notifications
├── activity_log/      # Audit log of user actions
├── static/            # Static files
├── templates/         # Base, landing, registration templates
├── build.sh           # Render build script
├── render.yaml        # Render deployment config
├── .env.example       # Environment variables template
└── requirements.txt
```

---

## Management Commands

**Scheduled Notifications** (run via cron in production):

- `check_task_deadlines` — Create notifications for upcoming task deadlines (1 or 3 days before)
- `check_order_day` — Create reminders when order delivery date is today
- `check_lead_no_order` — Remind agents about leads with no orders in last 30 days

**Setup / Sample Data**

- `create_categories` — Create product categories and subcategories
- `create_sample_products` — Create sample product data
- `update_products_for_dashboard` — Update product data for dashboard
- `create_default_categories` — Create default lead categories (e.g. Unassigned)

**Maintenance / Migration**

- `clean_duplicate_categories` — Remove duplicate lead categories
- `update_product_descriptions_english` — Update sample product descriptions to English
- `reassign_products_to_organisor` — Move products from one organisation to another

**Development / Test** (dev/test environments only)

- `create_test_data` — Create test data for leads
- `create_fake_notifications` — Create fake notifications for testing
- `final_cleanup` — Lead data cleanup
- `force_clean_duplicates` — Force clean duplicate lead categories

---

## Testing

```bash
python manage.py test
```

---

## Admin

URL: `http://127.0.0.1:8000/admin/` — Login with superuser credentials.

---

## Security

- Never commit `.env` or secrets. Only `.env.example` is committed; copy it to `.env` and fill in your values locally.
- Use environment variables for production
- Enable HTTPS in production

---

## License

MIT License — see [LICENSE](LICENSE) for details.
