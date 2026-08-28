[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md
version = 1.0.1
requirements = python3,kivy==2.2.1,arabic-reshaper,python-bidi,setuptools,wheel,six,pillow

orientation = portrait
fullscreen = 0

android.presplash_color = #FFFFFF
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,VIBRATE,CHANGE_NETWORK_STATE

android.api = 33
android.minapi = 31
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True
android.allow_backup = False
android.release_artifact = apk
android.debuggable = 0

android.signing.keystore = tasbihnoor.keystore
android.signing.alias = tasbihnoor

[buildozer]
log_level = 2
warn_on_root = 0
