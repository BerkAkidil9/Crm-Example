# Darkenyas CRM - Django Customer Relationship Management

A Django-based CRM system with email verification and authentication features.

## Features

- ✅ User authentication (username/email login)
- ✅ Email verification system
- ✅ Lead management
- ✅ Agent management
- ✅ Product and stock management
- ✅ Order management
- ✅ Financial reporting

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd env
```

### 2. Create virtual environment
```bash
python -m venv venv
# On Windows:
Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure settings
Edit `djcrm/settings.py` and replace the placeholder values:

```python
# Replace with your actual values
SECRET_KEY = 'your-actual-secret-key-here'
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-gmail-app-password"
```

### 5. Setup database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## Email Configuration

To enable email verification:

1. **Enable 2-Step Verification** in your Gmail account
2. **Generate App Password**:
   - Go to Google Account → Security → App passwords
   - Select Mail → Other → "Django CRM"
   - Copy the 16-character code
3. **Update settings.py** with your email and app password

## Admin Access

- URL: `http://127.0.0.1:8000/admin/`
- Login with your superuser credentials

## Project Structure

```
env/
├── agents/          # Agent management
├── djcrm/          # Main Django project
├── finance/        # Financial reporting
├── leads/          # Lead management & authentication
├── orders/         # Order management
├── ProductsAndStock/ # Product management
├── static/         # Static files
├── templates/      # HTML templates
└── manage.py       # Django management script
```

## Security Notes

- Never commit sensitive information to version control
- Use environment variables or secure config for production
- Keep your SECRET_KEY and email passwords secure
- Enable HTTPS in production

## License

This project is for educational/personal use.
