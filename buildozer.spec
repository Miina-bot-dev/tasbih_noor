[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = org.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt
version = 1.0.0
requirements = python3,kivy==2.2.1,arabic-reshaper,python-bidi,setuptools,wheel,six,pillow
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.keystore = ./release.keystore
android.keyalias = tasbihnoor

[buildozer]
log_level = 2
warn_on_root = 0
