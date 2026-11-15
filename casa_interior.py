import math, pygame
from config import *

def dibujar_interior(pantalla, t):
    pygame.draw.rect(pantalla, (110, 75, 45), (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pantalla, (80, 55, 30), (0, SUELO, ANCHO, 6))
    for x in range(0, ANCHO, 60):
        pygame.draw.line(pantalla, (90, 60, 35), (x, SUELO), (x - 15, ALTO), 2)

    pygame.draw.rect(pantalla, (150, 110, 75), (0, 0, ANCHO, SUELO))
    for x in range(0, ANCHO, 50):
        pygame.draw.line(pantalla, (135, 95, 65), (x, 0), (x, SUELO), 2)

    for y in (60, 160, SUELO - 40):
        pygame.draw.rect(pantalla, (95, 60, 35), (0, y, ANCHO, 14))
        pygame.draw.rect(pantalla, (70, 45, 25), (0, y, ANCHO, 14), 2)

    # Cuadros
    for cx in (200, 400, 600):
        pygame.draw.rect(pantalla, (110, 70, 40), (cx - 40, 90, 80, 60))
        pygame.draw.rect(pantalla, (60, 40, 20), (cx - 40, 90, 80, 60), 3)
        pygame.draw.rect(pantalla, (200, 180, 140), (cx - 32, 98, 64, 44))

    # Mostrador de razas (al fondo a la derecha)
    pygame.draw.rect(pantalla, (140, 90, 55), (ANCHO - 200, SUELO - 100, 160, 100))
    pygame.draw.rect(pantalla, (95, 60, 35), (ANCHO - 200, SUELO - 100, 160, 100), 3)
    pygame.draw.rect(pantalla, (170, 115, 70), (ANCHO - 205, SUELO - 110, 170, 14))
    
    # Bola de cristal en el mostrador
    pygame.draw.circle(pantalla, (100, 200, 255), (ANCHO - 120, SUELO - 130), 20)
    pygame.draw.circle(pantalla, (200, 240, 255), (ANCHO - 125, SUELO - 135), 8)

    # Antorcha
    tx = 120
    parpadeo = math.sin(t / 100) * 3
    brillo = pygame.Surface((180, 180), pygame.SRCALPHA)
    for r in range(90, 0, -6):
        a = int(4 + (90 - r) / 2)
        pygame.draw.circle(brillo, (255, 160, 60, a), (90, 90), r)
    pantalla.blit(brillo, (tx - 90, SUELO - 300 - 90))
    pygame.draw.rect(pantalla, (60, 40, 30), (tx - 5, SUELO - 300, 10, 40))
    pygame.draw.polygon(pantalla, (240, 110, 20), [(tx - 11, SUELO - 306), (tx, SUELO - 350 - parpadeo * 2), (tx + 11, SUELO - 306)])
    pygame.draw.polygon(pantalla, (255, 220, 90), [(tx - 6, SUELO - 306), (tx, SUELO - 335 - parpadeo), (tx + 6, SUELO - 306)])

    # Puerta
    pygame.draw.rect(pantalla, (70, 45, 25), (30, SUELO - 140, 80, 140), border_top_left_radius=40, border_top_right_radius=40)
    pygame.draw.rect(pantalla, (40, 40, 50), (30, SUELO - 140, 80, 140), 4, border_top_left_radius=40, border_top_right_radius=40)
    for i in range(1, 4):
        ly = SUELO - 140 + i * 35
        pygame.draw.line(pantalla, (50, 30, 15), (36, ly), (104, ly), 2)

    pygame.font.init()
    f = pygame.font.SysFont(None, 24)
    txt = f.render("W: Salir", True, (255, 230, 150))
    pantalla.blit(txt, (70 - txt.get_width() // 2, SUELO - 180))

def dibujar_puerta_salida_brillo(pantalla, cerca, t):
    if not cerca: return
    pulso = int(40 + 25 * math.sin(t / 150))
    brillo = pygame.Surface((120, 170), pygame.SRCALPHA)
    pygame.draw.rect(brillo, (255, 240, 150, pulso), brillo.get_rect(), border_radius=40)
    pantalla.blit(brillo, (10, SUELO - 155))