[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.include_patterns = assets/*
version = 1.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a
icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 1
warn_on_root = 0
