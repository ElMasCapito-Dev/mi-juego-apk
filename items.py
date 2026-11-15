# items.py
ITEMS = {
    "cuero": {
        "nombre": "Cuero",
        "color": (150, 100, 60),
        "color_borde": (90, 60, 30),
        "forma": "rect",
        "descripcion": "Piel curtida de un bandido. Material basico.",
        "stackeable": True,
        "consumible": False,
        "efecto": None,
    },
    "escama_dragon": {
        "nombre": "Escama de dragon",
        "color": (190, 40, 50),
        "color_borde": (120, 20, 35),
        "forma": "rombo",
        "descripcion": "Escama endurecida por el fuego. Material raro.",
        "stackeable": True,
        "consumible": False,
        "efecto": None,
    },
    "corazon_dragon": {
        "nombre": "Corazon de dragon",
        "color": (220, 30, 40),
        "color_borde": (100, 10, 20),
        "forma": "corazon",
        "descripcion": "Aun late debilmente. Material legendario.",
        "stackeable": False,
        "consumible": False,
        "efecto": None,
    },
    "armadura_infernal": {
        "nombre": "Armadura infernal",
        "color": (80, 30, 40),
        "color_borde": (240, 120, 40),
        "forma": "armadura",
        "descripcion": "Forjada en el fuego del dragon. +50 Vida Max.",
        "stackeable": False,
        "consumible": False,
        "efecto": "vida_extra",
    },
    "espada_infernal": {
        "nombre": "Espada infernal",
        "color": (240, 110, 30),
        "color_borde": (120, 30, 20),
        "forma": "espada",
        "descripcion": "Forjada con el fuego de un dragon. Aumenta tu dano base. Presiona [Z] para habilidad especial.",
        "stackeable": False,
        "consumible": False,
        "efecto": "dano_extra",
    },
}

def nombre(item_id):
    return ITEMS.get(item_id, {}).get("nombre", item_id)

def es_stackeable(item_id):
    return ITEMS.get(item_id, {}).get("stackeable", False)

def es_consumible(item_id):
    return ITEMS.get(item_id, {}).get("consumible", False)

def info(item_id):
    return ITEMS.get(item_id, None)