import pygame

# HÉROE FRAME 1
HEROE_1 = [
    "...H..H...",
    "..KKKKKK..",
    ".KKKKKKKK.",
    ".KSSSSSSK.",
    ".KSESSESK.",
    "..SSSSSS..",
    "...RRRR...",
    "..RBBBBR..",
    ".SRBBBBRS.",
    ".SRBBBBRS.",
    "..BBBBBB..",
    "..LL..LL..",
    "..LL..LL..",
    ".LLL..LLL.",
]
# HÉROE FRAME 2
HEROE_2 = [
    "...H..H...",
    "..KKKKKK..",
    ".KKKKKKKK.",
    ".KSSSSSSK.",
    ".KSESSESK.",
    "..SSSSSS..",
    "...RRRR...",
    "..RBBBBR..",
    ".SRBBBBRS.",
    ".SRBBBBRS.",
    "..BBBBBB..",
    ".LL....LL.",
    ".LL....LL.",
    "LLL....LLL",
]
HEROE_PALETA = {
    "H": (240, 240, 240), "K": (30, 20, 40), "S": (240, 200, 160),
    "E": (0, 0, 0), "R": (200, 30, 30), "B": (60, 60, 90), "L": (40, 40, 50),
}

# --- ARMADURA DRAGÓN (Se superpone exactamente sobre el cuerpo) ---
ARMADURA_MAPA = [
    "...R..R...", # 0 Cuernos
    "..RRRRRR..", # 1 Casco
    ".RRRRRRRR.", # 2 Hombros
    ".RRRRRRRR.", # 3 Pecho alto
    ".REERRRREE.", # 4 Ojos rojos (E)
    "..RRRRRR..", # 5 Pecho medio
    "...RRRR...", # 6 Cintura
    "..RRRRRR..", # 7 Musleras
    ".RRRRRRRR.", # 8 Musleras
    ".RRRRRRRR.", # 9
    "..RRRRRR..", # 10
    "..RR..RR..", # 11 Botas
    "..RR..RR..", # 12
    ".RRR..RRR.", # 13
]
ARMADURA_PALETA = {
    "R": (150, 20, 30),   # Rojo oscuro de dragón
    "E": (255, 50, 50),   # Ojos rojos brillantes
}

# --- BANDIDO ---
BANDIDO_1 = [
    "....CCCC....", "...CCCCCC...", "..CCCCCCCC..", "..CCEECCEECC", "..CCCCCCCC..",
    "...CCCCCC...", "..CCCCCCCC..", ".CCCCCCCCCC.", ".CC.CCCC.CC.", ".CC.CCCC.CC.",
    "..C.CCCC.C..", "..C..CC..C..", "..C..CC..C..", ".CC..CC..CC.", ".CC..CC..CC.",
    "..C..CC..C..", "..C..CC..C..", "..C......C..", "..C......C..",
]
BANDIDO_2 = [
    "....CCCC....", "...CCCCCC...", "..CCCCCCCC..", "..CCEECCEECC", "..CCCCCCCC..",
    "...CCCCCC...", "..CCCCCCCC..", ".CCCCCCCCCC.", ".CC.CCCC.CC.", ".CC.CCCC.CC.",
    "..C.CCCC.C..", ".CC..CC..CC.", ".CC..CC..CC.", "CC...CC...CC", "CC...CC...CC",
    ".C...CC...C.", ".C...CC...C.", ".....CC.....", ".....CC.....",
]
BANDIDO_PALETA = {"C": (55, 45, 65), "E": (220, 30, 30)}

ESPADA_MAPA = [
    "..B..", ".BWB.", ".BWB.", ".BWB.", ".BWB.", ".BWB.", ".BWB.",
    ".BWB.", ".BWB.", ".BWB.", ".BWB.", "YYYYY", "..H..", "..H..", "..P..",
]
ESPADA_PALETA = {
    "B": (190, 190, 210), "W": (245, 245, 255), "Y": (240, 200, 40), "H": (110, 60, 40), "P": (240, 200, 40),
}

ESCALA_DRAGON = 8
DRAGON_MAPA = [
    ".W.W....................", ".GGGG.......O.O.O.......", "GGEGGG.....DDDDDDDD.....",
    "KGGGGGGGGGGGGGGGGGGD....", "WWGGGGGGGGGGGGGGGGGGDD..", ".WWGGGGGBBBBBBBBGGGGDD..",
    "..GGGGGGBBBBBBBBGGGGDD..", "...GGGGGGGGGGGGGGDDD....", "....GG.GG.......GG.GG...",
    "....GG.GG.......GG.GG...", "...WWW.WWW.....WWW.WWW..",
]
DRAGON_PALETA = {
    "G": (190, 40, 50), "D": (120, 20, 35), "B": (245, 200, 120),
    "W": (240, 240, 225), "K": (20, 10, 10), "E": (255, 230, 40), "O": (240, 130, 30),
}

def crear_sprite(mapa, paleta, escala):
    h, w = len(mapa), len(mapa[0])
    s = pygame.Surface((w * escala, h * escala), pygame.SRCALPHA)
    for y, fila in enumerate(mapa):
        for x, c in enumerate(fila):
            if c in paleta:
                pygame.draw.rect(s, paleta[c], (x * escala, y * escala, escala, escala))
    return s

# Sprites del héroe
SPRITE_HEROE_1 = crear_sprite(HEROE_1, HEROE_PALETA, 5)
SPRITE_HEROE_2 = crear_sprite(HEROE_2, HEROE_PALETA, 5)
SPRITE_HEROE_1_IZQ = pygame.transform.flip(SPRITE_HEROE_1, True, False)
SPRITE_HEROE_2_IZQ = pygame.transform.flip(SPRITE_HEROE_2, True, False)
SPRITE_HEROE = SPRITE_HEROE_1
SPRITE_HEROE_IZQ = SPRITE_HEROE_1_IZQ

# Sprites de la armadura (Creados con la misma escala de 5)
SPRITE_ARMADURA = crear_sprite(ARMADURA_MAPA, ARMADURA_PALETA, 5)
SPRITE_ARMADURA_IZQ = pygame.transform.flip(SPRITE_ARMADURA, True, False)

SPRITE_ESPADA = crear_sprite(ESPADA_MAPA, ESPADA_PALETA, 4)

# Sprites del bandido
ESCALA_BANDIDO = 4
SPRITE_BANDIDO_1 = crear_sprite(BANDIDO_1, BANDIDO_PALETA, ESCALA_BANDIDO)
SPRITE_BANDIDO_2 = crear_sprite(BANDIDO_2, BANDIDO_PALETA, ESCALA_BANDIDO)
SPRITE_BANDIDO_FLIP_1 = pygame.transform.flip(SPRITE_BANDIDO_1, True, False)
SPRITE_BANDIDO_FLIP_2 = pygame.transform.flip(SPRITE_BANDIDO_2, True, False)
BANDIDO_W, BANDIDO_H = SPRITE_BANDIDO_1.get_size()
SPRITE_ENEMIGO = SPRITE_BANDIDO_1

# Dragón
SPRITE_DRAGON = crear_sprite(DRAGON_MAPA, DRAGON_PALETA, ESCALA_DRAGON)
SPRITE_DRAGON_DER = pygame.transform.flip(SPRITE_DRAGON, True, False)
DRAGON_W, DRAGON_H = SPRITE_DRAGON.get_size()