
[app]
title = Aluminum Calculator
package.name = alumcalc
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Application icon
icon.filename = %(source.dir)s/icon.png

requirements = python3==3.11.9,kivy==2.3.0
orientation = portrait
fullscreen = 0

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
