[app]
title = Tasbih Noor
package.name = tasbihnoor
package.domain = org.mina
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt
version = 1.0.0
requirements = python3,kivy==2.2.1,arabic-reshaper,python-bidi,setuptools,wheel,six,pillow
orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.2.0

fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# ⬇️⬇️⬇️ اینا مهم هستن ⬇️⬇️⬇️
android.skip_update = True
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.ant_path = ~/.buildozer/android/platform/apache-ant-1.9.4

android.archs = arm64-v8a, armeabi-v7a
p4a.branch = develop

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 0
