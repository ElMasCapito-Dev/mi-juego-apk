[app]
title = Anime Multiverse
package.name = animemultiverse
package.domain = org.mitol
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Requisitos exactos para que Pygame no falle
requirements = python3==3.10.12,kivy==2.3.0,hostpython3==3.10.12,pyjnius==1.5.0,pygame

orientation = landscape
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
# Solo para celulares modernos (evita errores de compilación)
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Para que no falle por las mayúsculas o los espacios
android.presplash_color = #000000
android.allow_backup = True
