# راهنمای رفع مشکل CustomUser

## مشکل
خطای `ValueError: The field admin.LogEntry.user was declared with a lazy reference to 'main.customuser'` به این دلیل است که migration های قبلی (admin, authtoken) به User model قدیمی اشاره می‌کنند.

## راه حل

### گزینه 1: حذف دیتابیس و ساخت مجدد (پیشنهادی برای پروژه جدید)

```bash
# 1. حذف دیتابیس
rm db.sqlite3

# 2. اجرای migration ها
python manage.py migrate

# 3. ایجاد superuser جدید
python manage.py createsuperuser
```

### گزینه 2: Fake unapply و reapply migration ها (اگر داده مهم دارید)

```bash
# 1. Fake unapply migration های مشکل‌دار
python manage.py migrate admin zero --fake
python manage.py migrate authtoken zero --fake

# 2. اجرای migration های main
python manage.py migrate main

# 3. اجرای مجدد migration های admin و authtoken
python manage.py migrate admin --fake-initial
python manage.py migrate authtoken --fake-initial
```

### گزینه 3: استفاده از --run-syncdb (برای پروژه جدید)

```bash
# 1. حذف دیتابیس
rm db.sqlite3

# 2. ساخت دیتابیس از نو
python manage.py migrate --run-syncdb

# 3. ایجاد superuser
python manage.py createsuperuser
```

## نکات مهم

- اگر داده مهمی در دیتابیس دارید، از گزینه 2 استفاده کنید
- برای پروژه جدید، گزینه 1 ساده‌تر است
- بعد از رفع مشکل، مطمئن شوید که `AUTH_USER_MODEL = 'main.CustomUser'` در settings.py تنظیم شده است

