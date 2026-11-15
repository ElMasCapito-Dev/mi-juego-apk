import pygame
from config import *
from sprites import (
    SPRITE_BANDIDO_1, SPRITE_BANDIDO_2,
    SPRITE_BANDIDO_FLIP_1, SPRITE_BANDIDO_FLIP_2,
    BANDIDO_W, BANDIDO_H,
)


class Enemigo:
    def __init__(self, x, hp, particulas=None):
        self.x = float(x)
        self.hp = hp
        self.hp_max = hp
        self.atk_t = 0
        self.particulas = particulas

        # Animación
        self.anim_t = 0
        self.frame = 0
        self.mirando_izq = True
        self.bob = 0.0

        # Efecto de ataque
        self.flash_ataque = 0   # frames restantes del flash gris

    @property
    def rect(self):
        return pygame.Rect(int(self.x), SUELO - BANDIDO_H, BANDIDO_W, BANDIDO_H)

    def recibir_golpe(self, dano, empuje):
        self.hp -= dano
        self.x += empuje
        if self.particulas:
            cx, cy = self.rect.center
            self.particulas.emitir(
                cx, cy,
                [(220, 220, 220), (180, 180, 180), (140, 140, 140)],
                5, vel=3, vida=15, tam=4)

    def actualizar(self, jugador, zona):
        r = self.rect
        # Movimiento hacia el jugador
        if r.centerx < jugador.rect.centerx - 5:
            self.x += 1.5
            self.mirando_izq = False
        elif r.centerx > jugador.rect.centerx + 5:
            self.x -= 1.5
            self.mirando_izq = True

        # Animación de caminar (solo si se mueve)
        se_mueve = abs(r.centerx - jugador.rect.centerx) > 8
        if se_mueve:
            self.anim_t += 1
            if self.anim_t >= 12:      # cambia de frame cada 12 frames
                self.anim_t = 0
                self.frame = 1 - self.frame
            # Bob vertical suave
            self.bob = abs(pygame.math.Vector2(1, 0).rotate(self.anim_t * 30).y) * 1.2
        else:
            self.frame = 0
            self.bob = 0

        # Ataque
        if r.inflate(30, 0).colliderect(jugador.rect):
            self.atk_t += 1
            if self.atk_t >= 60:
                self.atk_t = 0
                jugador.recibir_dano(2 + zona)
                self._emitir_golpe_gris(jugador)
        else:
            self.atk_t = 0

        if self.flash_ataque > 0:
            self.flash_ataque -= 1

    def _emitir_golpe_gris(self, jugador):
        """Onda de partículas grises al golpear."""
        cx = (self.rect.centerx + jugador.rect.centerx) // 2
        cy = (self.rect.centery + jugador.rect.centery) // 2
        if self.particulas:
            self.particulas.emitir(
                cx, cy,
                [(180, 180, 180), (140, 140, 140), (100, 100, 100), (220, 220, 220)],
                14, vel=5.0, vida=22, tam=6, gravedad=0.15)
        self.flash_ataque = 10

    def dibujar(self, pantalla, cam_x):
        sx = self.x - cam_x
        if sx < -100 or sx > ANCHO + 100:
            return

        # Elegir sprite según frame y dirección
        if self.mirando_izq:
            sprite = SPRITE_BANDIDO_1 if self.frame == 0 else SPRITE_BANDIDO_2
        else:
            sprite = SPRITE_BANDIDO_FLIP_1 if self.frame == 0 else SPRITE_BANDIDO_FLIP_2

        ey = SUELO - BANDIDO_H - int(self.bob)
        pantalla.blit(sprite, (sx, ey))

        # Flash gris cuando ataca
        if self.flash_ataque > 0:
            k = self.flash_ataque / 10
            radio = int(30 + 30 * (1 - k))
            alpha = int(180 * k)
            flash_surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (200, 200, 200, alpha),
                               (radio, radio), radio, 3)
            pantalla.blit(flash_surf,
                          (sx + BANDIDO_W // 2 - radio,
                           ey + BANDIDO_H // 2 - radio))

        # Barra de vida
        pygame.draw.rect(pantalla, ROJO, (sx, ey - 10, BANDIDO_W, 5))
        pygame.draw.rect(pantalla, VERDE,
                         (sx, ey - 10,
                          BANDIDO_W * max(self.hp, 0) / self.hp_max, 5))