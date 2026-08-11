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
android.archs = arm64-v8a
icon.filename = %(source.dir)s/icon.png
android.sign = True
android.keystore = tasbih-release.keystore
android.keystore_alias = tasbih-key
android.keystore_keypass = 123456
android.keystore_storepass = 123456

[buildozer]
log_level = 1
warn_on_root = 0
