[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
[buildozer]
log_level = 2
warn_on_root = 1
