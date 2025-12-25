# راهنمای سریع شروع

## 🚀 نصب سریع

```bash
# 1. نصب وابستگی‌ها
pip install -r requirements.txt

# 2. کپی فایل environment
cp .env.example .env

# 3. ویرایش .env و تنظیم OPENAI_API_KEY
nano .env  # یا ویرایشگر مورد علاقه شما

# 4. اجرای migration
python manage.py makemigrations
python manage.py migrate

# 5. اجرای سرور
python manage.py runserver
```

## 📝 تنظیمات ضروری در .env

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-your-openai-api-key
```

## 🔌 استفاده از API

### آپلود تصویر و دریافت فال

```bash
curl -X POST http://localhost:8000/api/v1/coffee-reading/ \
  -F "images=@/path/to/coffee-cup.jpg"
```

### مشاهده مستندات API

باز کردن مرورگر و رفتن به:
```
http://localhost:8000/api/docs/
```

## 🧹 پاکسازی فایل‌های قدیمی

```bash
# نمایش فایل‌هایی که حذف می‌شوند
python manage.py cleanup_old_files --days=30 --dry-run

# حذف فایل‌های قدیمی‌تر از 30 روز
python manage.py cleanup_old_files --days=30
```

## 🧪 اجرای تست‌ها

```bash
python manage.py test
```

## 📊 مشاهده لاگ‌ها

```bash
# لاگ‌های عمومی
tail -f logs/django.log

# لاگ‌های خطا
tail -f logs/django_error.log
```

## ⚙️ تنظیمات پیشرفته

برای تنظیمات بیشتر، به فایل `SETUP.md` مراجعه کنید.

