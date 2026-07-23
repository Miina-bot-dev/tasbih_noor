[app]
# نام برنامه در گوشی
title = ذکر شمار حرفه‌ای

# نام بسته (بدون فاصله و فارسی)
package.name = zekr_app
package.domain = ir.yourname.zekr

# فایل‌های ورودی
source.include_exts = py,png,jpg,ttf,json
source.include_patterns = assets/*,images/*

# نسخه برنامه (برای بازار مهم است)
version = 1.0.0

# نیازمندی‌ها (کتابخانه‌هایی که استفاده کردی)
requirements = python3,kivy,arabic_reshaper,python-bidi

# جهت صفحه (فقط عمودی برای اپ تسبیح بهتر است)
orientation = portrait

# آیکن (اگر فایل icon.png داری مسیرش را بده، در غیر این صورت این خط را کامنت کن)
# icon.filename = %(source.dir)s/icon.png

# تنظیمات اندروید
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# اجازه استفاده از فونت و فایل‌های محلی
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
