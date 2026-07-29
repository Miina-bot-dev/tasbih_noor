[app]
# عنوان اپلیکیشن
title = Zekr App
package.name = zekr_app
package.domain = ir.yourname.zekr

# مسیر سورس
source.dir = .

# پسوند فایل‌هایی که باید در اپلیکیشن گنجانده شوند
source.include_exts = py,png,jpg,ttf,json

# شامل کردن پوشه‌های دارایی‌ها
source.include_patterns = assets/*,images/*

version = 1.0.0

# اصلاح شده: حذف pillow برای عبور از مرحله کامپایل در گیت‌هاب
# این پیش‌نیازها برای نمایش صحیح فارسی ضروری هستند
requirements = python3,kivy,arabic_reshaper,python-bidi

orientation = portrait

# دسترسی‌ها
android.permissions = INTERNET

# تنظیمات اندروید (نسخه‌های پایدار برای GitHub Actions)
android.api = 33
android.minapi = 21
android.sdk = 33

# نسخه NDK پایدار
android.ndk = 25b

# اصلاح شده: محدود کردن به یک معماری برای کاهش فشار روی GitHub Actions و جلوگیری از خطا
android.archs = arm64-v8a

# پذیرش خودکار لایسنس‌ها
android.accept_sdk_license = True

android.allow_backup = True

[buildozer]
# سطح لاگ برای عیب‌یابی بهتر
log_level = 2
warn_on_root = 1
