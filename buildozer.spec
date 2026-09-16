[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md

# ارتقای نسخه برای اعمال به عنوان به‌روزرسانی معتبر
version = 1.0.4
version.code = 5
icon.filename = icon.png

# نیازمندی‌های استاندارد پایتون برای اندروید
requirements = python3,kivy==2.2.1,arabic-reshaper,setuptools,pillow

orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF

# حذف پرمیشن‌های حساس شبکه و حافظه جهت رفع اخطار گوگل
android.permissions = INTERNET,VIBRATE

android.api = 33
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21

# قفل روی تک‌معماری ۶۴ بیتی جهت افزایش سرعت بیلد
android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = False
android.release_artifact = apk
android.debuggable = 0

# 🌟 پچ طلایی: حذف خطوط امضای مستقیم در بیلدوزر برای جلوگیری از تداخل با امضای گیت‌هاب
# این کار باعث می‌شود بیلدوزر فایل خام بسازد و فایل yml شما آن را به صورت استاندارد امضا کند
android.signing.keystore = 
android.signing.alias = 

# استفاده از برنچ پایدار پایتون برای اندروید
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
