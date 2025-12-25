# راهنمای راه‌اندازی و پیکربندی

## 📋 مراحل اولیه

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2. تنظیم Environment Variables
```bash
cp .env.example .env
# سپس فایل .env را ویرایش کنید
```

### 3. اجرای Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. ایجاد Superuser (اختیاری)
```bash
python manage.py createsuperuser
```

### 5. اجرای سرور
```bash
python manage.py runserver
```

## 🔧 پیکربندی پیشرفته

### Rate Limiting

Rate limiting به صورت خودکار فعال است و درخواست‌ها را به 10 درخواست در دقیقه برای هر IP محدود می‌کند.

برای تغییر این مقدار، در فایل `.env`:
```
RATE_LIMIT_PER_MINUTE=20
```

### File Cleanup

برای پاکسازی خودکار فایل‌های قدیمی، می‌توانید از management command استفاده کنید:

```bash
# نمایش فایل‌هایی که حذف می‌شوند (بدون حذف واقعی)
python manage.py cleanup_old_files --days=30 --dry-run

# حذف فایل‌های قدیمی‌تر از 30 روز
python manage.py cleanup_old_files --days=30

# حذف فایل‌های قدیمی‌تر از 7 روز
python manage.py cleanup_old_files --days=7
```

### تنظیم Cron Job برای Cleanup خودکار

برای اجرای خودکار cleanup، می‌توانید یک cron job اضافه کنید:

```bash
# ویرایش crontab
crontab -e

# اضافه کردن این خط برای اجرای روزانه در ساعت 2 صبح
0 2 * * * cd /path/to/forecast_back && /path/to/venv/bin/python manage.py cleanup_old_files --days=30 >> /var/log/cleanup.log 2>&1
```

یا می‌توانید از systemd timer استفاده کنید:

**فایل: `/etc/systemd/system/forecast-cleanup.service`**
```ini
[Unit]
Description=Forecast Back File Cleanup
After=network.target

[Service]
Type=oneshot
User=your-user
WorkingDirectory=/path/to/forecast_back
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python manage.py cleanup_old_files --days=30
```

**فایل: `/etc/systemd/system/forecast-cleanup.timer`**
```ini
[Unit]
Description=Run Forecast Back File Cleanup Daily
Requires=forecast-cleanup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

سپس:
```bash
sudo systemctl enable forecast-cleanup.timer
sudo systemctl start forecast-cleanup.timer
```

## 🧪 اجرای Tests

```bash
# اجرای تمام تست‌ها
python manage.py test

# اجرای تست‌های یک app خاص
python manage.py test main

# اجرای یک تست خاص
python manage.py test main.tests.FileModelTest
```

## 📊 Monitoring

### لاگ‌ها

لاگ‌ها در پوشه `logs/` ذخیره می‌شوند:
- `logs/django.log`: لاگ‌های عمومی
- `logs/django_error.log`: لاگ‌های خطا

برای مشاهده لاگ‌ها:
```bash
# مشاهده لاگ‌های عمومی
tail -f logs/django.log

# مشاهده لاگ‌های خطا
tail -f logs/django_error.log
```

### بررسی وضعیت

```bash
# بررسی تنظیمات Django
python manage.py check

# بررسی تنظیمات امنیتی
python manage.py check --deploy
```

## 🚀 Deployment

### با Gunicorn

```bash
gunicorn forecast_back.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### با Nginx

**فایل: `/etc/nginx/sites-available/forecast_back`**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/forecast_back/staticfiles/;
    }

    location /media/ {
        alias /path/to/forecast_back/media/;
    }
}
```

### Environment Variables در Production

مطمئن شوید که در Production:
- `DEBUG=False`
- `SECRET_KEY` یک مقدار امن و تصادفی است
- `ALLOWED_HOSTS` به دامنه‌های مجاز محدود شده است
- `OPENAI_API_KEY` تنظیم شده است

## 🔒 امنیت

1. **HTTPS**: در Production حتماً از HTTPS استفاده کنید
2. **SECRET_KEY**: هرگز SECRET_KEY را در Git commit نکنید
3. **ALLOWED_HOSTS**: فقط دامنه‌های مجاز را اضافه کنید
4. **Rate Limiting**: فعال است و می‌توانید مقدار آن را تنظیم کنید
5. **CORS**: فقط origin‌های مجاز را در `CORS_ALLOWED_ORIGINS` اضافه کنید

## 📝 نکات مهم

- قبل از Production، حتماً `DEBUG=False` تنظیم کنید
- فایل `.env` را هرگز در Git commit نکنید
- لاگ‌ها را به صورت منظم بررسی کنید
- فایل‌های قدیمی را به صورت منظم پاکسازی کنید
- از backup منظم دیتابیس استفاده کنید

