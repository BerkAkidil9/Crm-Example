# Darkenyas CRM

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

A multi-tenant Django CRM with role-based access for organisations and agents.

---

## Tech Stack

Django 5.0 · Python 3.12 · Tailwind CSS · Crispy Forms · WhiteNoise · Gunicorn · django-phonenumber-field

**Database:** SQLite (default, development) / PostgreSQL (production)

---

## Features

### Roles

| Role | Access |
|------|--------|
| **Administrator** | Full system: all organisors, agents, leads, products, orders, finance, tasks, activity log |
| **Organisor** | Own organisation: profile, agents, leads, products, orders, finance, tasks, activity within org |
| **Agent** | Assigned leads, own orders, personal tasks, notifications, activity affecting them |

### Modules

| Module | Features |
|--------|----------|
| **Leads** | CRUD, agent assignment; source & value categories; profile photo, phone; activity history; org/agent filters |
| **Agents** | CRUD, profile (photo, phone); list by organisation |
| **Organisors** | Organisation CRUD; Admin manages all, Organisor manages own profile |
| **Products & Stock** | Category/subcategory; stock levels, minimum threshold; discounts (%, fixed, date range); bulk price update; sales dashboard; charts; stock movements; price history; stock alerts (low/out/overstock); stock recommendations |
| **Orders** | Orders linked to leads; product line items; auto stock reduce on order; stock restore on cancel; org/agent filters |
| **Finance** | Date range reports; filter by `creation_date` or `order_day`; org/agent filters; earnings, cost, profit |
| **Tasks** | Status, priority; assign to agents; org/agent filters; notifications: task assigned, order created, lead assigned, deadline reminders |
| **Activity Log** | Audit trail for leads, orders, tasks, agents, organisors, products; org/agent filters |

### Authentication

Signup · Email verification · Login (email or username) · Password reset · Profile photo · Phone number

---

## Quick Start

**Prerequisites:** Python 3.12+

```bash
# 1. Clone
git clone <your-repo-url>
cd Crm-Example

# 2. Virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Environment
cp .env.example .env
# Edit .env: SECRET_KEY, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# 5. Database
python manage.py migrate
python manage.py createsuperuser

# 6. Run
python manage.py runserver
```

Open `http://127.0.0.1:8000/`

**PostgreSQL:** Set `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` in `.env`.

---

## Email Configuration

For signup verification and password reset:

1. Enable **2-Step Verification** in your Gmail account  
2. Create an **App Password**: Google Account → Security → App passwords → Mail → Other  
3. Add to `.env`: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

---

## Deploy on Render

Use the included `render.yaml` Blueprint:

- **Database:** PostgreSQL (from Render) → `DATABASE_URL` auto-set
- **Web:** Build runs `build.sh` (install, collectstatic, migrate, optional createsuperuser)
- **Env:** Set `SECRET_KEY` (generate), `DEBUG=False`; `RENDER_EXTERNAL_HOSTNAME` is automatic

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

**Reminders / Notifications** (run via cron for scheduled notifications):

- `check_task_deadlines` — Create notifications for upcoming task deadlines
- `check_order_day` — Create reminders for order dates
- `check_lead_no_order` — Remind agents about leads with no orders

**Products:**

- `create_categories` — Create product categories and subcategories
- `create_sample_products` — Create sample product data
- `update_products_for_dashboard` — Update product data for dashboard

**Leads:**

- `create_default_categories` — Create default lead categories (e.g. Unassigned)
- `clean_duplicate_categories` — Remove duplicate lead categories

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

- Never commit `.env` or secrets
- Use environment variables for production
- Enable HTTPS in production

---

## License

Educational / personal use.
