[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md
version = 1.0.4
version.code = 6
icon.filename = icon.png

requirements = python3,kivy==2.3.0,arabic-reshaper,setuptools

orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE

# ارتقا به اندروید ۱۴ برای حل مشکل سپر ایمنی و گوشی‌های جدید
android.api = 34
android.minapi = 21
android.ndk = 26b
android.ndk_api = 21

# سازگاری با معماری‌های ۳۲ و ۶۴ بیتی
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = False
android.release_artifact = apk
android.debuggable = 0

# تنظیمات کلید امضا
android.signing.keystore = tasbih-releser.keystore
android.signing.alias = tasbih-key

# ارتقا به نسخه پایدار پایتون برای اندروید جهت هماهنگی با اندروید ۱۴
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
