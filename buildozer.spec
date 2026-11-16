[app]
title = Anime Multiverse
package.name = animemultiverse
package.domain = org.mitol
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Aquí está la magia: versión de Python y Kivy exacta que sí funciona
requirements = python3,kivy==2.3.0,pygame,pyjnius

orientation = landscape
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
# Configuración vital para que no falle
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# ¡ESTO ES LO QUE FALTABA! Le decimos que ignore esos módulos rotos
android.skip_update = True
p4a.branch = master
p4a.bootstrap = sdl2
