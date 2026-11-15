import pygame
from config import *
from niveles import xp_necesaria

pygame.font.init()
fuente = pygame.font.SysFont(None, 32)
fuente_chica = pygame.font.SysFont(None, 24)
COLOR_TEXTO = (30, 30, 40)

HUD_FONDO = pygame.Surface((190, 200), pygame.SRCALPHA)
pygame.draw.rect(HUD_FONDO, (255, 255, 255, 150), HUD_FONDO.get_rect(), border_radius=10)

def texto(pantalla, msg, f, color, x, y):
    pantalla.blit(f.render(msg, True, color), (x, y))

def dibujar_hud(pantalla, datos, jugador):
    pantalla.blit(HUD_FONDO, (8, 8))
    texto(pantalla, f"Oro: {datos['oro']}", fuente, COLOR_TEXTO, 15, 15)
    texto(pantalla, f"Vida: {max(jugador.vida, 0)}/{jugador.vida_max}", fuente, COLOR_TEXTO, 15, 48)
    texto(pantalla, f"Nivel: {datos['nivel']}", fuente, COLOR_TEXTO, 15, 81)

    necesaria = xp_necesaria(datos["nivel"])
    pygame.draw.rect(pantalla, (240, 240, 240), (15, 114, 160, 10))
    pygame.draw.rect(pantalla, AZUL, (15, 114, 160 * datos["xp"] / necesaria, 10))
    pygame.draw.rect(pantalla, COLOR_TEXTO, (15, 114, 160, 10), 2)