ANCHO = 800
ALTO = 500
FPS = 60
TITULO = "Anime Multiverse"

# Física
SUELO = 380
GRAVEDAD = 0.8
SALTO = -15

# Combate
DURACION_GOLPE = 8

# Mapa
CASTILLO_X = 4500
CASTILLO_ANCHO = 1400
MAPA_LARGO = CASTILLO_X + CASTILLO_ANCHO
ZONA_PX = 1500

# Puerta del castillo
PUERTA_ANCHO = 100
PUERTA_ALTO = 160
PUERTA_X = CASTILLO_X + CASTILLO_ANCHO // 2 - PUERTA_ANCHO // 2

# ---- Casa de Aventura ----
CASA_X = 1400
CASA_ANCHO = 460
CASA_PUERTA_ANCHO = 70
CASA_PUERTA_ALTO = 120
CASA_PUERTA_X = CASA_X + CASA_ANCHO // 2 - CASA_PUERTA_ANCHO // 2

# ---- Herrería ----
HERRERIA_X = CASA_X + CASA_ANCHO + 80
HERRERIA_ANCHO = 460
HERRERIA_PUERTA_ANCHO = 70
HERRERIA_PUERTA_ALTO = 120
HERRERIA_PUERTA_X = HERRERIA_X + HERRERIA_ANCHO // 2 - HERRERIA_PUERTA_ANCHO // 2

# Dragón Jefe
DRAGON_HP = 400
DRAGON_RESPAWN = 60 * FPS

# Niveles y estadísticas
PUNTOS_POR_NIVEL = 3
COMBATE_DANO_POR_PUNTO = 2
COMBATE_VELOCIDAD_POR_PUNTO = 2
VIDA_POR_PUNTO = 20

# ---- Crafteo ----
ESPADA_INFER_ORO = 0
ESPADA_INFER_CORAZONES = 5
ESPADA_INFER_ESCAMAS = 50
ESPADA_INFER_DANO_EXTRA = 25

# ---- Armadura Infernal ----
ARMADURA_INFER_VIDA_EXTRA = 50

# ---- Habilidad Especial (Espada Infernal) ----
Z_COOLDOWN = 5 * FPS
Z_DANO = 40
Z_RADIO = 150
PODER_DANO_HABILIDAD = 10

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (200, 30, 30)
AZUL = (60, 120, 220)
VERDE = (40, 180, 90)
AMARILLO = (240, 200, 40)
GRIS = (200, 200, 200)

# ---- Sistema de Razas ----
# La suma total de "prob" da 1000 (1000 = 100.0%)
RAZAS = {
    "humano":  {"nombre": "Humano",  "desc": "+20 Vida Max", 
                "color": (200, 180, 150), "prob": 0},
    
    "dragon":  {"nombre": "Dragón",  "desc": "+15% Daño · [T] Transformación + Vuelo + Fuego",
                "color": (200, 50, 50),   "prob": 5},       # 0.5%
    
    "kitsune": {"nombre": "Kitsune", "desc": "+20% Vel, +15% Esquiva · [T] Transformación",
                "color": (240, 140, 50), "prob": 50},      # 5%
    
    "demonio": {"nombre": "Demonio", "desc": "+10% Daño, Robo de Vida · [T] Transformación",
                "color": (150, 30, 50),  "prob": 50},      # 5%
    
    "angel":   {"nombre": "Ángel",   "desc": "+10% Vida, +5% Esquiva",
                "color": (240, 240, 200), "prob": 100},    # 10%
    
    "hada":    {"nombre": "Hada",    "desc": "+15% Velocidad",
                "color": (255, 150, 200), "prob": 150},    # 15%
    
    "elfo":    {"nombre": "Elfo",    "desc": "+10% Daño, +5% Velocidad",
                "color": (120, 200, 120), "prob": 150},    # 15%
    
    "lobo":    {"nombre": "Lobo",    "desc": "+15% Velocidad",
                "color": (150, 120, 100), "prob": 250},    # 25%
    
    "ave":     {"nombre": "Ave",     "desc": "+20% Velocidad, Salto Alto",
                "color": (100, 200, 255), "prob": 245},    # 24.5%
    
    "zombie":  {"nombre": "Zombie",  "desc": "Lento pero con mucha vida",
                "color": (100, 150, 100), "prob": 0},      # 0%
}
COSTO_GEMAS_RAZA = 500

# ---- Kitsune ----
KITSUNE_VEL_BONUS      = 1.20
KITSUNE_ESQUIVA        = 0.15
KITSUNE_TRANS_CD       = 5 * FPS
KITSUNE_TRANS_VEL      = 1.30
KITSUNE_TRANS_DANO     = 1.30

# ---- Dragón ----
DRAGON_VEL_BONUS       = 1.05
DRAGON_TRANS_CD        = 5 * FPS
DRAGON_TRANS_VEL       = 1.10
DRAGON_TRANS_DANO      = 1.40
DRAGON_TRANS_VIDA      = 1.30
DRAGON_VUELO_SUBIR     = -0.9
DRAGON_VUELO_MAX_UP    = -9.0
DRAGON_VUELO_GRAVEDAD  = 0.25
DRAGON_BOLA_CD         = int(0.6 * FPS)
DRAGON_BOLA_DANO       = 35
DRAGON_BOLA_VEL        = 9.0
DRAGON_BOLA_VIDA       = 90

# ---- Demonio ----
DEMONIO_TRANS_CD       = 5 * FPS
DEMONIO_TRANS_VEL      = 1.20
DEMONIO_TRANS_DANO     = 1.25
DEMONIO_TRANS_VIDA     = 1.15

DEMONIO_BOLA_CD        = int(0.6 * FPS)
DEMONIO_BOLA_DANO      = 35
DEMONIO_BOLA_VEL       = 10.0
DEMONIO_BOLA_VIDA      = 80

# ---- Precios del Comerciante (en gemas) ----
PRECIOS_VENTA = {
    "corazon_dragon": 100,
    "armadura_infernal": 200,
    "cuero": 2,
    "escama_dragon": 10,
}

# Si es True, muestra botones en pantalla (celular). Se activa automáticamente.
ES_MOVIL = False