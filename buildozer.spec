[app]
title = Aluminum Calculator
package.name = alumcalc
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
# Pin the Python version that is known to work
requirements = python3==3.11.9,kivy==2.3.0
orientation = portrait
fullscreen = 0
# Use a single architecture for faster builds and fewer errors
android.archs = arm64-v8a
android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.accept_sdk_license = True
android.allow_backup = True
android.permissions =
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1