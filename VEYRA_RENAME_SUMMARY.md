# خلاصه تغییرات نام اپلیکیشن به Veyra

## تغییرات انجام شده

### 1. Package Name (نام پکیج)
- **قبل**: `com.hagaseca.thost9`
- **بعد**: `com.veyra.app`

**فایل‌های به‌روزرسانی شده:**
- ✅ `android/app/build.gradle` - namespace و applicationId
- ✅ `android/app/src/main/AndroidManifest.xml` - package و MainActivity reference
- ✅ `android/app/google-services.json` - package_name
- ✅ `android/app/src/main/kotlin/com/veyra/app/MainActivity.kt` - package name و انتقال فایل

### 2. App Name (نام اپلیکیشن)
- **قبل**: `forecast_app`
- **بعد**: `Veyra`

**فایل‌های به‌روزرسانی شده:**
- ✅ `android/app/src/main/AndroidManifest.xml` - android:label
- ✅ `web/manifest.json` - name و short_name
- ✅ `pubspec.yaml` - name و description

### 3. Package Imports (واردات پکیج)
- **قبل**: `package:forecast_app/...`
- **بعد**: `package:veyra/...`

**فایل‌های به‌روزرسانی شده:**
- ✅ `lib/core/services/ad_service.dart`
- ✅ `lib/coffee.dart`
- ✅ `lib/horoscope.dart`
- ✅ `lib/tarot.dart`
- ✅ `test/widget_test.dart`
- ✅ `android/test/widget_test.dart`

### 4. فایل‌های منتقل شده
- ✅ `MainActivity.kt` از `com/hagaseca/thost9/` به `com/veyra/app/` منتقل شد

## وضعیت فعلی

### ✅ تکمیل شده
- Package name در تمام فایل‌های Android
- نام اپلیکیشن در AndroidManifest و Web manifest
- تمام importهای Dart به‌روزرسانی شدند
- MainActivity به پکیج جدید منتقل شد
- pubspec.yaml به‌روزرسانی شد

### ⚠️ نیاز به توجه
1. **Firebase Console**: باید یک Android app جدید با package name `com.veyra.app` اضافه کنید و `google-services.json` جدید را دانلود کنید
2. **iOS Bundle ID**: اگر iOS هم می‌سازید، باید Bundle ID را در Xcode تغییر دهید
3. **App Store/Play Store**: اگر اپ قبلاً منتشر شده، باید نام جدید را در store listings به‌روزرسانی کنید

## مراحل بعدی

### برای Firebase:
1. به [Firebase Console](https://console.firebase.google.com/) بروید
2. پروژه `forecast-281f3` را انتخاب کنید
3. **Project Settings** > **Your apps** > **Add app** > **Android**
4. Package name: `com.veyra.app`
5. `google-services.json` جدید را دانلود کنید
6. فایل را در `android/app/google-services.json` جایگزین کنید

### برای تست:
```bash
cd forecast_app
flutter clean
flutter pub get
flutter build apk --debug
```

## فایل‌های تغییر یافته

### Android
- `android/app/build.gradle`
- `android/app/src/main/AndroidManifest.xml`
- `android/app/google-services.json`
- `android/app/src/main/kotlin/com/veyra/app/MainActivity.kt` (جدید)

### Flutter/Dart
- `pubspec.yaml`
- `lib/core/services/ad_service.dart`
- `lib/coffee.dart`
- `lib/horoscope.dart`
- `lib/tarot.dart`
- `test/widget_test.dart`
- `android/test/widget_test.dart`

### Web
- `web/manifest.json`

## نکات مهم
- ✅ تمام تغییرات اعمال شد
- ✅ هیچ خطای کامپایلی وجود ندارد
- ⚠️ Firebase باید دوباره تنظیم شود
- ✅ اپلیکیشن آماده بیلد است

