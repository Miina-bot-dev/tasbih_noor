[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = com.tasbihnoor.app

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md

version = 1.0.1
version.code = 2

requirements = python3,kivy==2.2.1,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0

android.presplash_color = #FFFFFF
android.permissions = INTERNET,VIBRATE,ACCESS_NETWORK_STATE

android.api = 34
android.minapi = 21
android.ndk = 27c
android.ndk_api = 21
android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = False
android.debuggable = 1

p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0
