from guardado import guardar

# Definición estática de misiones
MISIONES = {
    "bandidos": {
        "titulo": "Mision 1: Mata 5 bandidos",
        "objetivo_total": 5,
        "recompensa_oro": 500,
        "recompensa_xp": 600,
    },
    "dragon": {
        "titulo": "Mision 2: Mata al dragon",
        "objetivo_total": 1,
        "recompensa_oro": 1000,
        "recompensa_xp": 2000,
    },
}


def asegurar_campos(datos):
    """Añade los campos de misiones al diccionario de guardado si no existen."""
    if "mision_activa" not in datos:
        datos["mision_activa"] = None
    if "mision_progreso" not in datos:
        datos["mision_progreso"] = 0


def puede_aceptar(datos):
    return datos["mision_activa"] is None


def aceptar(datos, clave):
    if not puede_aceptar(datos):
        return False
    if clave not in MISIONES:
        return False
    datos["mision_activa"] = clave
    datos["mision_progreso"] = 0
    guardar(datos)
    return True


def progreso(datos, clave, cantidad=1):
    """Suma progreso si la misión activa coincide."""
    asegurar_campos(datos)
    if datos["mision_activa"] == clave:
        datos["mision_progreso"] += cantidad
        if datos["mision_progreso"] > MISIONES[clave]["objetivo_total"]:
            datos["mision_progreso"] = MISIONES[clave]["objetivo_total"]


def completada(datos):
    asegurar_campos(datos)
    clave = datos["mision_activa"]
    if clave is None:
        return False
    return datos["mision_progreso"] >= MISIONES[clave]["objetivo_total"]


def entregar(datos):
    """Devuelve (oro, xp) y limpia la misión activa. Si no está completa, (0,0)."""
    from niveles import ganar_xp  # import local para evitar ciclos
    asegurar_campos(datos)
    if not completada(datos):
        return (0, 0)
    clave = datos["mision_activa"]
    oro = MISIONES[clave]["recompensa_oro"]
    xp = MISIONES[clave]["recompensa_xp"]
    datos["oro"] += oro
    ganar_xp(datos, xp)
    datos["mision_activa"] = None
    datos["mision_progreso"] = 0
    guardar(datos)
    return (oro, xp)