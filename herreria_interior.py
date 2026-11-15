import math, pygame
from config import *


def dibujar_interior(pantalla, t):
    """Interior de la herrería: yunque, fuego, herramientas."""
    # Suelo de piedra
    pygame.draw.rect(pantalla, (60, 55, 55), (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pantalla, (35, 30, 30), (0, SUELO, ANCHO, 6))
    for x in range(0, ANCHO, 70):
        pygame.draw.line(pantalla, (45, 40, 40), (x, SUELO), (x - 20, ALTO), 2)

    # Pared trasera
    pygame.draw.rect(pantalla, (75, 70, 75), (0, 0, ANCHO, SUELO))
    for fila, y in enumerate(range(0, SUELO, 28)):
        pygame.draw.line(pantalla, (55, 50, 55), (0, y), (ANCHO, y), 2)
        off = 28 if fila % 2 else 0
        for x in range(off, ANCHO, 56):
            pygame.draw.line(pantalla, (55, 50, 55), (x, y),
                             (x, min(y + 28, SUELO)), 2)

    # Chimenea con fuego a la derecha
    ch_x = ANCHO - 180
    ch_y = SUELO - 260
    pygame.draw.rect(pantalla, (50, 45, 50), (ch_x, ch_y, 100, 260))
    pygame.draw.rect(pantalla, (30, 25, 30), (ch_x, ch_y, 100, 260), 4)
    # Fuego
    parp = math.sin(t / 80) * 6
    pygame.draw.polygon(pantalla, (240, 100, 20), [
        (ch_x + 20, SUELO - 60), (ch_x + 50, SUELO - 160 - parp),
        (ch_x + 80, SUELO - 60)])
    pygame.draw.polygon(pantalla, (255, 180, 40), [
        (ch_x + 30, SUELO - 60), (ch_x + 50, SUELO - 120 - parp),
        (ch_x + 70, SUELO - 60)])
    pygame.draw.polygon(pantalla, (255, 240, 120), [
        (ch_x + 40, SUELO - 60), (ch_x + 50, SUELO - 90 - parp),
        (ch_x + 60, SUELO - 60)])

    # Yunque en el centro-derecha
    ax = ANCHO // 2 + 40
    ay = SUELO - 60
    pygame.draw.rect(pantalla, (40, 40, 45), (ax, ay, 30, 60))
    pygame.draw.rect(pantalla, (70, 70, 75), (ax - 10, ay - 25, 100, 25))
    pygame.draw.rect(pantalla, (90, 90, 95), (ax - 10, ay - 25, 100, 8))
    pygame.draw.polygon(pantalla, (70, 70, 75), [
        (ax - 10, ay), (ax + 90, ay), (ax + 70, ay + 20), (ax + 10, ay + 20)])

    # Herramientas en la pared
    for hx in (120, 220):
        pygame.draw.line(pantalla, (120, 80, 40), (hx, SUELO - 280),
                         (hx, SUELO - 220), 4)
        pygame.draw.rect(pantalla, (140, 140, 150),
                         (hx - 10, SUELO - 220, 20, 14))

    # Puerta de salida (izquierda)
    pygame.draw.rect(pantalla, (50, 40, 40), (30, SUELO - 140, 80, 140),
                     border_top_left_radius=40, border_top_right_radius=40)
    pygame.draw.rect(pantalla, (20, 20, 25), (30, SUELO - 140, 80, 140), 4,
                     border_top_left_radius=40, border_top_right_radius=40)
    for i in range(1, 4):
        ly = SUELO - 140 + i * 35
        pygame.draw.line(pantalla, (30, 25, 25), (36, ly), (104, ly), 2)

    pygame.font.init()
    f = pygame.font.SysFont(None, 24)
    txt = f.render("W: Salir", True, (255, 230, 150))
    pantalla.blit(txt, (70 - txt.get_width() // 2, SUELO - 180))


def dibujar_puerta_salida_brillo(pantalla, cerca, t):
    if not cerca:
        return
    pulso = int(40 + 25 * math.sin(t / 150))
    brillo = pygame.Surface((120, 170), pygame.SRCALPHA)
    pygame.draw.rect(brillo, (255, 240, 150, pulso), brillo.get_rect(),
                     border_radius=40)
    pantalla.blit(brillo, (10, SUELO - 155))