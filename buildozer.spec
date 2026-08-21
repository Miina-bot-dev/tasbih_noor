[app]

# (str) Title of your application
title = Tasbih Noor

# (str) Package name
package.name = tasbihnoor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mina

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy==2.2.1,arabic-reshaper,python-bidi,setuptools,wheel,six,pillow

# (list) Supported orientations
orientation = portrait

#
# OSX Specific
#

osx.python_version = 3
osx.kivy_version = 2.2.0

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
# Using NDK r25b for better stability with buildozer
android.ndk = 25b

# (int) Android NDK API to use.
android.ndk_api = 21

# (bool) If True, then skip trying to update the Android sdk
# This avoids excess Internet downloads and prevents HTTP 502 errors
android.skip_update = True

# (list) Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use
# Using develop branch for updated download URLs and better compatibility
p4a.branch = develop

#
# iOS specific
#

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
