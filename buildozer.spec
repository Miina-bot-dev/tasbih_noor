[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = org.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy,jdatetime,arabic_reshaper,python_bidi
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 23b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
