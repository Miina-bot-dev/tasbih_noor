[app]

# (string) Title of your application
title = Tasbih Noor

# (string) Package name
package.name = tasbihnoor

# (string) Package domain (needed for android packaging)
package.domain = com.tasbihnoor.app

# (string) Source code directory
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json,txt,md

# (string) Application version
version = 1.0.2

# (int) Application version code (numeric)
# این عدد برای اینکه بازار و مایکت فایل را به عنوان آپدیت قبول کنند بالا برده شد
version.code = 3

# (str) Icon of the application
# اصلاح آدرس مستقیم آیکون بر اساس فایل ریشه گیت‌هاب شما
icon.filename = icon.png

# (list) Application requirements
# حذف پکیج‌های بیودی و سیکس برای جلوگیری از کرش موتور متنی اندروید
requirements = python3,kivy==2.2.1,arabic-reshaper,setuptools,wheel,pillow

# (str) Supported orientations (valid options are: landscape, portrait or all)
orientation = portrait

# (int) Fullscreen mode, 0 or 1
fullscreen = 0

# (string) Presplash background color (for android)
android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,VIBRATE,CHANGE_NETWORK_STATE

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 27c

# (int) Android NDK API to use
android.ndk_api = 21

# (list) Architectures to build for
android.archs = arm64-v8a,armeabi-v7a

# (bool) Accept SDK license without prompting
android.accept_sdk_license = True

# (bool) Allow Android app to participate in backup infrastructure
android.allow_backup = False

# (str) Format used to package the app for release (apk or aab)
android.release_artifact = apk

# (int) Debuggable mode
android.debuggable = 0

# (str) Path to your keystore for signing
android.signing.keystore = tasbih-releser.keystore

# (str) Alias name in your keystore
android.signing.alias = tasbih-key

# (str) python-for-android branch to use
p4a.branch = v2024.01.21

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug and big outputs)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 0
