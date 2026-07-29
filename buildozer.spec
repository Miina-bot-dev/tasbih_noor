[app]
source.dir = .

title = ذکر شمار حرفه‌ای
package.name = zekr_app
package.domain = ir.yourname.zekr

source.include_exts = py,png,jpg,ttf,json
source.include_patterns = assets/*,images/*

version = 1.0.0

requirements = python3,kivy,arabic_reshaper,python-bidi

orientation = portrait

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
