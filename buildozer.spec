[app]
title = Zekr App
package.name = zekr_app
package.domain = ir.yourname.zekr
source.dir = .
source.include_exts = py,png,jpg,ttf,json
version = 1.0.0
requirements = python3,kivy,arabic_reshaper,python-bidi
orientation = portrait
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 0
