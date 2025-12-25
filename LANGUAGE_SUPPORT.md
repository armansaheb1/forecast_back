# راهنمای پشتیبانی چندزبانه

## 🌍 زبان‌های پشتیبانی شده

سیستم از زبان‌های زیر پشتیبانی می‌کند:

- **fa** - فارسی (پیش‌فرض)
- **en** - English
- **ar** - العربية
- **tr** - Türkçe
- **az** - Azərbaycan
- **ru** - Русский

## 🔧 نحوه کار

### 1. تنظیم زبان کاربر

کاربران می‌توانند زبان مورد نظر خود را در پروفایل تنظیم کنند:

```json
PATCH /api/v1/auth/profile/
{
  "language": "en"
}
```

### 2. استفاده در API فال قهوه

#### روش 1: استفاده از زبان کاربر (پیشنهادی)
اگر کاربر لاگین باشد، به صورت خودکار از زبان تنظیم شده در پروفایل استفاده می‌شود.

```bash
POST /api/v1/coffee-reading/
Authorization: Token <user_token>
Content-Type: multipart/form-data

images: <image_file>
```

#### روش 2: ارسال زبان در درخواست
می‌توانید زبان را مستقیماً در درخواست ارسال کنید (این مقدار بر زبان کاربر اولویت دارد):

```bash
POST /api/v1/coffee-reading/
Content-Type: multipart/form-data

images: <image_file>
language: en
```

#### روش 3: استفاده از Header
اگر کاربر لاگین نباشد و زبان در درخواست ارسال نشده باشد، سیستم از `Accept-Language` header استفاده می‌کند:

```bash
POST /api/v1/coffee-reading/
Accept-Language: en-US,en;q=0.9,fa;q=0.8
Content-Type: multipart/form-data

images: <image_file>
```

### 3. اولویت انتخاب زبان

1. **زبان ارسال شده در request body** (بالاترین اولویت)
2. **زبان تنظیم شده در پروفایل کاربر** (اگر لاگین باشد)
3. **Accept-Language header** (اگر ارسال شده باشد)
4. **فارسی (fa)** (پیش‌فرض)

## 📝 مثال‌های استفاده

### مثال 1: فال به زبان انگلیسی

```bash
curl -X POST http://localhost:8000/api/v1/coffee-reading/ \
  -H "Authorization: Token <token>" \
  -F "images=@coffee.jpg" \
  -F "language=en"
```

### مثال 2: فال به زبان عربی

```bash
curl -X POST http://localhost:8000/api/v1/coffee-reading/ \
  -H "Authorization: Token <token>" \
  -F "images=@coffee.jpg" \
  -F "language=ar"
```

### مثال 3: استفاده از زبان کاربر

```bash
# ابتدا زبان را در پروفایل تنظیم کنید
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"language": "tr"}'

# سپس فال بگیرید (به صورت خودکار به ترکی خواهد بود)
curl -X POST http://localhost:8000/api/v1/coffee-reading/ \
  -H "Authorization: Token <token>" \
  -F "images=@coffee.jpg"
```

## 📤 Response

Response شامل فیلد `language` است که نشان می‌دهد فال به چه زبانی تولید شده:

```json
{
  "file": {
    "id": 1,
    "image": "/media/coffee/image.jpg",
    "image_url": "http://localhost:8000/media/coffee/image.jpg",
    "user": 1,
    "user_username": "john",
    "created_at": "2025-02-09T21:00:00Z",
    "updated_at": "2025-02-09T21:00:00Z"
  },
  "reading": {
    "content": "متن فال قهوه به زبان انتخاب شده...",
    "role": "assistant"
  },
  "language": "fa"
}
```

## 🔄 تغییر زبان در پروفایل

کاربران می‌توانند زبان خود را در هر زمان تغییر دهند:

```bash
PATCH /api/v1/auth/profile/
Authorization: Token <token>
Content-Type: application/json

{
  "language": "en"
}
```

## 📱 استفاده در اپ موبایل

### iOS (Swift)
```swift
let url = URL(string: "http://your-api.com/api/v1/coffee-reading/")!
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("Token \(userToken)", forHTTPHeaderField: "Authorization")

let boundary = UUID().uuidString
request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

var body = Data()
// Add image
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"images\"; filename=\"coffee.jpg\"\r\n".data(using: .utf8)!)
body.append(imageData)
// Add language
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"language\"\r\n\r\n".data(using: .utf8)!)
body.append("en".data(using: .utf8)!)
body.append("--\(boundary)--\r\n".data(using: .utf8)!)

request.httpBody = body
```

### Android (Kotlin)
```kotlin
val requestBody = MultipartBody.Builder()
    .setType(MultipartBody.FORM)
    .addFormDataPart("images", "coffee.jpg", 
        RequestBody.create(MediaType.parse("image/jpeg"), imageFile))
    .addFormDataPart("language", "en")
    .build()

val request = Request.Builder()
    .url("http://your-api.com/api/v1/coffee-reading/")
    .addHeader("Authorization", "Token $userToken")
    .post(requestBody)
    .build()
```

## ⚙️ تنظیمات پیشرفته

### اضافه کردن زبان جدید

برای اضافه کردن زبان جدید، فایل `main/language_utils.py` را ویرایش کنید:

```python
LANGUAGE_PROMPTS = {
    # ... زبان‌های موجود
    'new_lang': {
        'system': "System prompt in new language",
        'user': "User prompt in new language"
    },
}
```

سپس در `main/models.py` به `LANGUAGE_CHOICES` اضافه کنید:

```python
LANGUAGE_CHOICES = [
    # ... انتخاب‌های موجود
    ('new_lang', 'New Language Name'),
]
```

## 🔍 نکات مهم

1. اگر زبان نامعتبر ارسال شود، از زبان پیش‌فرض (فارسی) استفاده می‌شود
2. فال همیشه به زبان انتخاب شده تولید می‌شود
3. زبان در response برگردانده می‌شود تا اپ موبایل بداند فال به چه زبانی است
4. تغییر زبان در پروفایل بر تمام فال‌های بعدی تأثیر می‌گذارد

