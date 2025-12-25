# Coffee Reading API (Forecast Back)

API برای فال قهوه با استفاده از OpenAI GPT-4o Vision Model

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8+
- pip
- virtualenv (پیشنهادی)

### مراحل نصب

1. **کلون کردن پروژه** (اگر از Git استفاده می‌کنید)
```bash
git clone <repository-url>
cd forecast_back
```

2. **ایجاد محیط مجازی**
```bash
python -m venv env
source env/bin/activate  # در Windows: env\Scripts\activate
```

3. **نصب وابستگی‌ها**
```bash
pip install -r requirements.txt
```

4. **تنظیم متغیرهای محیطی**
```bash
cp .env.example .env
```

سپس فایل `.env` را ویرایش کرده و مقادیر زیر را تنظیم کنید:
- `SECRET_KEY`: یک کلید مخفی Django (می‌توانید از `python manage.py shell` و سپس `from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())` استفاده کنید)
- `OPENAI_API_KEY`: کلید API OpenAI خود را وارد کنید
- `ALLOWED_HOSTS`: لیست هاست‌های مجاز (با کاما جدا کنید)
- `MEDIA_ROOT_URL`: آدرس پایه برای دسترسی به فایل‌های رسانه (مثلاً: `http://localhost:8000`)

5. **اجرای Migration**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **ایجاد Superuser (اختیاری)**
```bash
python manage.py createsuperuser
```

7. **اجرای سرور**
```bash
python manage.py runserver
```

## 📚 API Documentation

پس از راه‌اندازی سرور، می‌توانید مستندات API را در آدرس زیر مشاهده کنید:
- Swagger UI: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`

## 🔌 Endpoints

### POST `/api/v1/coffee-reading`
آپلود تصویر فنجان قهوه و دریافت فال

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `images`: فایل تصویر (JPEG, PNG, WebP - حداکثر 10MB)

**Response:**
```json
{
  "file": {
    "id": 1,
    "image": "/media/coffee/image.jpg",
    "image_url": "http://localhost:8000/media/coffee/image.jpg",
    "created_at": "2025-02-09T21:00:00Z",
    "updated_at": "2025-02-09T21:00:00Z"
  },
  "reading": {
    "content": "متن فال قهوه...",
    "role": "assistant"
  }
}
```

## 🔒 امنیت

- تمام تنظیمات حساس از طریق متغیرهای محیطی مدیریت می‌شوند
- در Production، `DEBUG=False` تنظیم کنید
- `ALLOWED_HOSTS` را محدود کنید
- از HTTPS استفاده کنید
- API Key را هرگز در کد قرار ندهید

## 📝 Logging

لاگ‌ها در پوشه `logs/` ذخیره می‌شوند:
- `logs/django.log`: لاگ‌های عمومی
- `logs/django_error.log`: لاگ‌های خطا

## 🛠️ توسعه

### اجرای Tests
```bash
python manage.py test
```

### بررسی کد
```bash
python manage.py check
```

## 📦 وابستگی‌ها

- Django 5.1+
- Django REST Framework
- django-cors-headers
- python-decouple
- drf-spectacular
- openai
- Pillow

## 📄 License

[لطفاً License خود را اینجا قرار دهید]

