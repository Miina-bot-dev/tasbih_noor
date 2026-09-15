[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md
version = 1.0.3
version.code = 6
icon.filename = icon.png

requirements = python3,kivy==2.3.1,arabic-reshaper,setuptools

orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE
android.api = 34
android.minapi = 21
android.ndk = 25c
android.ndk_api = 21
# هر دو معماری تا رو همهٔ گوشی‌ها (32 و 64 بیتی) نصب بشه
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = False
android.release_artifact = apk
android.debuggable = 0
android.signing.keystore = tasbih-releser.keystore
android.signing.alias = tasbih-key
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
