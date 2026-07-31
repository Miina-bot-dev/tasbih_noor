[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = org.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy,arabic_reshaper,python-bidi,sdl2_ttf
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools = 33.0.0
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
