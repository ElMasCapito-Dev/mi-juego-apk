from config import PUNTOS_POR_NIVEL


def xp_necesaria(nivel):
    return 40 + 20 * nivel


def ganar_xp(datos, cantidad):
    datos["xp"] += cantidad
    # while, por si una sola subida de XP alcanza para varios niveles
    while datos["xp"] >= xp_necesaria(datos["nivel"]):
        datos["xp"] -= xp_necesaria(datos["nivel"])
        datos["nivel"] += 1
        datos["puntos"] += PUNTOS_POR_NIVEL