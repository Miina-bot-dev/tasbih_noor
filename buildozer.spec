[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md
# نسخه را نسبت به انتشار قبلی خود چک کنید؛ در حال حاضر روی ۱.۰.۳ تنظیم شده
version = 1.0.3
version.code = 4

# 🖼️ بخش آیکون: مطمئن شوید فایلی به نام icon.png با ابعاد 512x512 در کنار main.py وجود دارد
icon.filename = %(source.dir)s/icon.png

# 📚 نیازمندی‌ها: برای جلوگیری از تداخل، اجازه دهید بیلدوزر بهترین نسخه پایتون را خودش انتخاب کند
requirements = python3,kivy==2.2.1,arabic-reshaper,pillow,setuptools

orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF

# ⚠️ مجوزها: دسترسی‌های اضافی که مارکت‌ها روی آن حساس هستند و خطای ناامن می‌دهند حذف شدند
android.permissions = INTERNET,VIBRATE,ACCESS_NETWORK_STATE

# 🔐 سازگاری کامل با اندرویدهای جدید (رفع خطای ناسازگاری بازار و گوگل‌پلی)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = False
android.release_artifact = apk

# 🛠️ تنظیمات امضای تجاری برای بازار و مایکت (توکن‌های گیت‌هاب اکشنز)
android.debuggable = 0
android.keystore = %(source.dir)s/tasbih-releser.keystore
android.keystore.password = ${{ secrets.KEYSTORE_PASSWORD }}
android.keyalias = tasbih-key
android.keyalias.password = ${{ secrets.KEY_PASSWORD }}

p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
