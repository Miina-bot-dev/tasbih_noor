[app]
# عنوان اپلیکیشن (بدون کاراکتر فارسی در اینجا بهتر است، اما در کد نمایش دهیم)
title = Zekr App
package.name = zekr_app
package.domain = ir.yourname.zekr

# مسیر سورس (نقطه یعنی همین پوشه)
source.dir = .

# پسوند فایل‌هایی که باید در اپلیکیشن گنجانده شوند
source.include_exts = py,png,jpg,ttf,json

# اگر پوشه assets یا images داری، حتماً این‌ها را نگه دار
source.include_patterns = assets/*,images/*

version = 1.0.0

# پیش‌نیازها: اضافه کردن بسیار مهم python-bidi و arabic_reshaper برای نمایش درست متن فارسی
# همچنین اضافه کردن pillow (برای کار با تصاویر) بسیار توصیه می‌شود
requirements = python3,kivy,arabic_reshaper,python-bidi,pillow

orientation = portrait

# دسترسی‌ها
android.permissions = INTERNET

# تنظیمات اندروید (نسخه‌های پایدار برای GitHub Actions)
android.api = 33
android.minapi = 21
android.sdk = 33

# نسخه NDK را روی حالت پیش‌فرض یا یک نسخه بسیار پایدار می‌گذاریم تا بیلد در گیت‌هاب با خطا مواجه نشود
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# بسیار مهم: پذیرش خودکار لایسنس‌ها
android.accept_sdk_license = True

android.allow_backup = True

[buildozer]
# سطح لاگ را روی 2 بگذار تا اگر خطا داد، ما بتوانیم در گیت‌هاب جزئیات را ببینیم
log_level = 2
warn_on_root = 1
