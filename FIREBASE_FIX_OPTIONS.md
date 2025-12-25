# Firebase Package Name Fix - راه‌حل‌های رفع مشکل

## مشکل
پکیج نیم از `com.example.forecast` به `com.hagaseca.thost9` تغییر کرده، اما Firebase هنوز اپلیکیشن قدیمی را می‌شناسد.

## راه‌حل ۱: اضافه کردن اپلیکیشن جدید در Firebase (توصیه می‌شود)

1. به [Firebase Console](https://console.firebase.google.com/) بروید
2. پروژه `forecast-281f3` را انتخاب کنید
3. به **Project Settings** > **Your apps** بروید
4. روی **Add app** > **Android** کلیک کنید
5. Package name را `com.hagaseca.thost9` وارد کنید
6. `google-services.json` جدید را دانلود کنید
7. فایل قدیمی را جایگزین کنید: `/forecast_back/forecast_app/android/app/google-services.json`

## راه‌حل ۲: موقتاً غیرفعال کردن Google Services (اگر Firebase ضروری نیست)

اگر می‌خواهید سریع بیلد کنید و بعداً Firebase را تنظیم کنید:

1. در `android/app/build.gradle` خط 6 را کامنت کنید:
```gradle
plugins {
    id "com.android.application"
    id 'kotlin-android'
    id 'kotlin-kapt'
    id "dev.flutter.flutter-gradle-plugin"
    // id "com.google.gms.google-services"  // موقتاً غیرفعال
}
```

2. بیلد کنید:
```bash
flutter clean
flutter pub get
flutter build apk --debug
```

3. بعداً وقتی Firebase را تنظیم کردید، کامنت را بردارید.

## راه‌حل ۳: استفاده از package name قدیمی (اگر نمی‌خواهید Firebase را تغییر دهید)

اگر می‌خواهید از package name قدیمی استفاده کنید:

1. `android/app/build.gradle` را تغییر دهید:
```gradle
namespace 'com.example.forecast'
applicationId "com.example.forecast"
```

2. `AndroidManifest.xml` را تغییر دهید:
```xml
package="com.example.forecast"
```

3. MainActivity را به `com.example.forecast` منتقل کنید

## وضعیت فعلی
- ✅ `google-services.json` به‌روزرسانی شد (package name: `com.hagaseca.thost9`)
- ⚠️ باید در Firebase Console هم اپلیکیشن جدید اضافه شود

