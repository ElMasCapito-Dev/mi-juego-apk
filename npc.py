import math, pygame
from config import *

pygame.font.init()
_fuente = pygame.font.SysFont(None, 22)

class NPC:
    def __init__(self, x, nombre="Anciano", tipo="anciano"):
        self.x = x
        self.nombre = nombre
        self.tipo = tipo
        self.rect = pygame.Rect(x, SUELO - 70, 40, 70)

    def cerca(self, jugador):
        return abs(jugador.rect.centerx - self.rect.centerx) < 90 and jugador.en_suelo

    def dibujar(self, pantalla, t):
        r = self.rect
        pygame.draw.ellipse(pantalla, (60, 40, 30), (r.x - 4, r.bottom - 8, r.w + 8, 12))

        if self.tipo == "comerciante": self._dibujar_comerciante(pantalla, r, t)
        elif self.tipo == "herrero": self._dibujar_herrero(pantalla, r, t)
        else: self._dibujar_anciano(pantalla, r, t)

        txt = _fuente.render(f"{self.nombre} [E]", True, (255, 240, 150))
        tx = r.centerx - txt.get_width() // 2
        ty = r.y - 34 + int(math.sin(t / 200) * 3)
        pantalla.blit(_fuente.render(f"{self.nombre} [E]", True, (0, 0, 0)), (tx + 1, ty + 1))
        pantalla.blit(txt, (tx, ty))

    def _dibujar_anciano(self, pantalla, r, t):
        pygame.draw.polygon(pantalla, (110, 70, 130), [(r.centerx - 20, r.bottom), (r.centerx + 20, r.bottom), (r.centerx + 14, r.y + 30), (r.centerx - 14, r.y + 30)])
        pygame.draw.circle(pantalla, (230, 195, 160), (r.centerx, r.y + 22), 14)
        pygame.draw.polygon(pantalla, (220, 220, 220), [(r.centerx - 12, r.y + 26), (r.centerx + 12, r.y + 26), (r.centerx, r.y + 50)])
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx - 4, r.y + 20), 2)
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx + 4, r.y + 20), 2)
        pygame.draw.line(pantalla, (90, 60, 30), (r.x - 6, r.bottom), (r.x - 4, r.y + 10), 4)

    def _dibujar_comerciante(self, pantalla, r, t):
        pygame.draw.polygon(pantalla, (40, 120, 60), [(r.centerx - 20, r.bottom), (r.centerx + 20, r.bottom), (r.centerx + 14, r.y + 30), (r.centerx - 14, r.y + 30)])
        pygame.draw.line(pantalla, (240, 200, 40), (r.centerx, r.y + 34), (r.centerx, r.bottom - 4), 3)
        pygame.draw.circle(pantalla, (230, 195, 160), (r.centerx, r.y + 22), 14)
        pygame.draw.rect(pantalla, (60, 40, 30), (r.centerx - 8, r.y + 28, 16, 6))
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx - 4, r.y + 20), 2)
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx + 4, r.y + 20), 2)
        mon_y = r.y + 10 + int(math.sin(t / 250) * 3)
        pygame.draw.circle(pantalla, (240, 200, 40), (r.x - 8, mon_y), 5)
        pygame.draw.circle(pantalla, (160, 120, 20), (r.x - 8, mon_y), 5, 1)

    def _dibujar_herrero(self, pantalla, r, t):
        pygame.draw.polygon(pantalla, (90, 60, 35), [(r.centerx - 18, r.bottom), (r.centerx + 18, r.bottom), (r.centerx + 12, r.y + 32), (r.centerx - 12, r.y + 32)])
        pygame.draw.circle(pantalla, (220, 170, 130), (r.centerx, r.y + 22), 14)
        pygame.draw.polygon(pantalla, (80, 50, 30), [(r.centerx - 12, r.y + 26), (r.centerx + 12, r.y + 26), (r.centerx, r.y + 48)])
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx - 4, r.y + 20), 2)
        pygame.draw.circle(pantalla, (0, 0, 0), (r.centerx + 4, r.y + 20), 2)
        pygame.draw.rect(pantalla, (110, 60, 30), (r.x - 10, r.y + 10, 6, 40))
        pygame.draw.rect(pantalla, (100, 100, 110), (r.x - 14, r.y + 8, 14, 10))