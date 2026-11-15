import math, pygame
from config import *


def dibujar_interior(pantalla, t):
    """Dibuja el interior del castillo: sala oscura con antorchas."""
    # Suelo
    pygame.draw.rect(pantalla, (60, 55, 60), (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pantalla, (40, 35, 40), (0, SUELO, ANCHO, 6))

    # Baldosas del suelo
    for x in range(0, ANCHO, 80):
        pygame.draw.line(pantalla, (50, 45, 50), (x, SUELO), (x - 20, ALTO), 2)
    for y in range(SUELO + 20, ALTO, 30):
        pygame.draw.line(pantalla, (50, 45, 50), (0, y), (ANCHO, y), 1)

    # Pared trasera
    pygame.draw.rect(pantalla, (45, 40, 50), (0, 0, ANCHO, SUELO))
    for y in range(0, SUELO, 26):
        for x in range(0, ANCHO, 52):
            off = 26 if (y // 26) % 2 else 0
            pygame.draw.rect(pantalla, (55, 50, 60),
                             (x + off, y, 50, 24), 1)

    # Antorchas en las paredes
    for tx in (80, ANCHO - 80):
        parpadeo = math.sin(t / 100 + tx) * 3
        brillo = pygame.Surface((180, 180), pygame.SRCALPHA)
        for r in range(90, 0, -6):
            a = int(4 + (90 - r) / 2)
            pygame.draw.circle(brillo, (255, 160, 60, a), (90, 90), r)
        pantalla.blit(brillo, (tx - 90, SUELO - 240 - 90))
        pygame.draw.rect(pantalla, (60, 40, 30), (tx - 5, SUELO - 240, 10, 40))
        pygame.draw.rect(pantalla, (90, 90, 100), (tx - 11, SUELO - 246, 22, 10))
        pygame.draw.polygon(pantalla, (240, 110, 20), [
            (tx - 11, SUELO - 246),
            (tx, SUELO - 290 - parpadeo * 2),
            (tx + 11, SUELO - 246)])
        pygame.draw.polygon(pantalla, (255, 220, 90), [
            (tx - 6, SUELO - 246),
            (tx, SUELO - 275 - parpadeo),
            (tx + 6, SUELO - 246)])

    # Puerta de salida (izquierda)
    pygame.draw.rect(pantalla, (70, 45, 25), (30, SUELO - 160, 90, 160),
                     border_top_left_radius=45, border_top_right_radius=45)
    pygame.draw.rect(pantalla, (40, 40, 50), (30, SUELO - 160, 90, 160), 4,
                     border_top_left_radius=45, border_top_right_radius=45)
    for i in range(1, 4):
        ly = SUELO - 160 + i * 40
        pygame.draw.line(pantalla, (50, 30, 15), (36, ly), (114, ly), 2)

    # Texto "W: Salir"
    pygame.font.init()
    f = pygame.font.SysFont(None, 24)
    txt = f.render("W: Salir", True, (255, 230, 150))
    pantalla.blit(txt, (75 - txt.get_width() // 2, SUELO - 200))


def dibujar_puerta_salida_brillo(pantalla, cerca, t):
    if not cerca:
        return
    pulso = int(40 + 25 * math.sin(t / 150))
    brillo = pygame.Surface((130, 190), pygame.SRCALPHA)
    pygame.draw.rect(brillo, (255, 240, 150, pulso), brillo.get_rect(),
                     border_radius=45)
    pantalla.blit(brillo, (10, SUELO - 175))