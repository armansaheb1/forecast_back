# راه‌حل سریع برای رفع خطای Build

## مشکل
```
No matching client found for package name 'com.hagaseca.thost9' in google-services.json
```

## راه‌حل سریع (اگر Firebase فعلاً ضروری نیست)

اگر می‌خواهید سریع بیلد کنید و بعداً Firebase را تنظیم کنید:

### مرحله 1: غیرفعال کردن Google Services Plugin

فایل `android/app/build.gradle` را باز کنید و خط 6 را کامنت کنید:

```gradle
plugins {
    id "com.android.application"
    id 'kotlin-android'
    id 'kotlin-kapt'
    id "dev.flutter.flutter-gradle-plugin"
    // id "com.google.gms.google-services"  // موقتاً غیرفعال
}
```

### مرحله 2: بیلد کنید

```bash
cd forecast_app
flutter clean
flutter pub get
flutter build apk --debug
```

### مرحله 3: بعداً Firebase را تنظیم کنید

1. به Firebase Console بروید
2. یک Android app جدید با package name `com.hagaseca.thost9` اضافه کنید
3. `google-services.json` جدید را دانلود کنید
4. فایل را در `android/app/` قرار دهید
5. کامنت را از `build.gradle` بردارید

## راه‌حل کامل (اگر Firebase ضروری است)

1. به [Firebase Console](https://console.firebase.google.com/) بروید
2. پروژه `forecast-281f3` را انتخاب کنید
3. **Project Settings** > **Your apps** > **Add app** > **Android**
4. Package name: `com.hagaseca.thost9`
5. `google-services.json` را دانلود کنید
6. فایل را در `android/app/google-services.json` جایگزین کنید
7. بیلد کنید

## وضعیت فعلی
- ✅ Package name در `build.gradle` و `AndroidManifest.xml` به‌روزرسانی شد
- ✅ `google-services.json` به‌روزرسانی شد (اما Firebase Console باید هم تنظیم شود)
- ⚠️ برای بیلد موفق، باید یکی از راه‌حل‌های بالا را انجام دهید

