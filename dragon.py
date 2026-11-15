import math, random, pygame
from config import *
from sprites import SPRITE_DRAGON, SPRITE_DRAGON_DER, DRAGON_W, DRAGON_H, ESCALA_DRAGON

pygame.font.init()
fuente_boss = pygame.font.SysFont(None, 20)
TEXTO_BOSS = fuente_boss.render("BOSS", True, (225, 30, 30))
SOMBRA_BOSS = fuente_boss.render("BOSS", True, (0, 0, 0))

E = ESCALA_DRAGON
MX, MY = 130, 110
ALTURA_VUELO = 150

ARENA_IZQ = CASTILLO_X + 120
ARENA_DER = MAPA_LARGO - 120 - DRAGON_W
ARENA_INT_IZQ = 120
ARENA_INT_DER = ANCHO - 120 - DRAGON_W

COLOR_ALA = (150, 25, 45)
COLOR_ALA_FONDO = (105, 18, 36)
BORDE_ALA = (235, 120, 30)

class BolaFuego:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.radio = 15
        self.vida = 300
        self.viva = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)

    def explotar(self, part):
        if part: part.emitir(self.x, self.y, [(255, 220, 90), (255, 130, 30), (200, 50, 20)], 16, vel=5, vida=25, tam=7, gravedad=0.1)
        self.viva = False

    def actualizar(self, jugador, part):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1
        if part: part.emitir(self.x, self.y, [(255, 200, 60), (255, 120, 30), (200, 50, 20)], 2, vel=1.0, vida=18, tam=7)
        if self.rect.colliderect(jugador.rect):
            jugador.recibir_dano(12)
            self.explotar(part)
        elif self.y >= SUELO - 6 or self.vida <= 0 or not (0 < self.x < MAPA_LARGO):
            self.explotar(part)

    def dibujar(self, pantalla, cam_x):
        sx, sy = int(self.x - cam_x), int(self.y)
        if sx < -50 or sx > ANCHO + 50: return
        r = self.radio + int(math.sin(pygame.time.get_ticks() / 60) * 2)
        pygame.draw.circle(pantalla, (200, 50, 20), (sx, sy), r + 4)
        pygame.draw.circle(pantalla, (255, 140, 30), (sx, sy), r)
        pygame.draw.circle(pantalla, (255, 230, 120), (sx, sy), max(2, int(r * 0.5)))

class Dragon:
    def __init__(self, particulas):
        self.part = particulas
        self.bolas = []
        self.recien_derrotado = False
        self.sacudir = 0
        self.en_interior = False
        self.reiniciar()

    def reiniciar(self):
        self.estado = "dormido"
        self.hp = DRAGON_HP
        self.x = float(ANCHO // 2 - DRAGON_W // 2) if self.en_interior else float(MAPA_LARGO - 420)
        self.y = float(SUELO - DRAGON_H)
        self.mirando_izq = True
        self.t = 0
        self.t_estado = 0
        self.vy = 0.0
        self.flash = 0
        self.alpha = 255
        self.timer_disparo = 90
        self.timer_picada = 420
        self.cargando = 0
        self.lado = 1
        self.lado_t = 0
        self.fase = 0
        self.destino = (0, 0)
        self.bolas.clear()

    def reposicionar_para_interior(self):
        self.en_interior = True
        self.reiniciar()

    def reposicionar_para_mundo(self):
        self.en_interior = False
        self.reiniciar()

    @property
    def rect(self):
        return pygame.Rect(int(self.x) + 10, int(self.y), DRAGON_W - 20, DRAGON_H)

    def vivo(self):
        return self.estado in ("dormido", "despertando", "combate", "cargando", "picada")

    def objetivos(self):
        return [self] if self.vivo() else []

    def boca(self):
        return (self.x + 4, self.y + 3.5 * E) if self.mirando_izq else (self.x + DRAGON_W - 4, self.y + 3.5 * E)

    def _limites(self):
        return (ARENA_INT_IZQ, ARENA_INT_DER) if self.en_interior else (ARENA_IZQ, ARENA_DER)

    def recibir_golpe(self, dano, empuje):
        if not self.vivo(): return
        if self.estado == "dormido":
            self.estado = "despertando"
            self.t_estado = 0
            self.sacudir = 24
        self.hp -= dano
        self.flash = 5
        cx, cy = self.rect.center
        if self.part: self.part.emitir(cx, cy, [(255, 80, 60), (255, 200, 80)], 6, vel=4, vida=20, tam=5)
        if self.hp <= 0:
            self.hp = 0
            self.estado = "caida"
            self.vy = 0.0
            self.bolas.clear()

    def actualizar(self, jugador, camara):
        self.t += 1
        self.t_estado += 1
        if self.flash > 0: self.flash -= 1
        px = jugador.rect.centerx

        if not self.en_interior:
            if self.estado in ("muerto", "cenizas"):
                if px < CASTILLO_X - 200: self.reiniciar()
            elif self.estado != "dormido" and px < CASTILLO_X + 80: self.reiniciar()

        for b in self.bolas[:]:
            b.actualizar(jugador, self.part)
            if not b.viva: self.bolas.remove(b)

        if self.estado == "dormido": self._dormido(px)
        elif self.estado == "despertando": self._despertando()
        elif self.estado in ("combate", "cargando", "picada"): self._pelear(jugador)
        elif self.estado == "caida": self._caida()
        elif self.estado == "cenizas": self._cenizas()

        if self.sacudir:
            camara.temblor = max(camara.temblor, self.sacudir)
            self.sacudir = 0

        if self.estado in ("combate", "cargando", "picada") and self.rect.colliderect(jugador.rect):
            jugador.recibir_dano(18 if (self.estado == "picada" and self.fase == 1) else 10)

    def _dormido(self, px):
        self.y = SUELO - DRAGON_H + math.sin(self.t / 30) * 2
        if self.t % 60 == 0 and self.part: self.part.emitir(self.boca()[0], self.boca()[1], [(160, 160, 160), (120, 120, 120)], 2, vel=0.5, vida=45, tam=6, gravedad=-0.03)
        if (self.en_interior and px > ANCHO / 2 - 200) or (not self.en_interior and px > CASTILLO_X + 300):
            self.estado = "despertando"
            self.t_estado = 0
            self.sacudir = 24

    def _despertando(self):
        k = min(1.0, self.t_estado / 80)
        self.y = (SUELO - DRAGON_H) + (ALTURA_VUELO - (SUELO - DRAGON_H)) * k
        if self.t_estado % 4 == 0 and self.part: self.part.emitir(self.boca()[0], self.boca()[1], [(255, 200, 60), (255, 120, 30)], 3, vel=3, vida=25, tam=6, gravedad=-0.08)
        if self.t_estado % 20 == 0: self.sacudir = 10
        if self.t_estado >= 80:
            self.estado = "combate"
            self.timer_disparo = 60
            self.timer_picada = 420

    def _volar_cerca(self, px):
        izq, der = self._limites()
        self.lado_t -= 1
        if self.lado_t <= 0:
            self.lado = random.choice([-1, 1])
            self.lado_t = random.randint(150, 260)
        meta_x = max(izq, min(der, px + self.lado * 260 - DRAGON_W / 2))
        self.x += max(-2.6, min(2.6, meta_x - self.x))
        self.y += (ALTURA_VUELO + math.sin(self.t / 35) * 30 - self.y) * 0.05

    def _pelear(self, jugador):
        px = jugador.rect.centerx
        picando = self.estado == "picada"
        if not (picando and self.fase == 1): self.mirando_izq = px < self.x + DRAGON_W / 2
        if not picando: self._volar_cerca(px)

        if self.estado == "combate":
            self.timer_disparo -= 1
            self.timer_picada -= 1
            if self.timer_picada <= 0:
                self.estado = "picada"
                self.fase = 0
                self.t_estado = 0
            elif self.timer_disparo <= 0:
                self.estado = "cargando"
                self.cargando = 28
        elif self.estado == "cargando":
            self.cargando -= 1
            if self.t % 3 == 0 and self.part: self.part.emitir(self.boca()[0], self.boca()[1], [(255, 200, 60), (255, 120, 30)], 2, vel=2, vida=15, tam=5)
            if self.cargando <= 0:
                self._disparar(jugador)
                self.estado = "combate"
                self.timer_disparo = int(110 - 50 * (1 - self.hp / DRAGON_HP))
        else: self._picada(jugador)

    def _disparar(self, jugador):
        bx, by = self.boca()
        ang = math.atan2(jugador.rect.centery - by, jugador.rect.centerx - bx)
        angulos = [ang] if self.hp >= DRAGON_HP / 2 else [ang - 0.28, ang, ang + 0.28]
        for a in angulos: self.bolas.append(BolaFuego(bx, by, math.cos(a) * 5.5, math.sin(a) * 5.5))
        if self.part: self.part.emitir(bx, by, [(255, 220, 90), (255, 120, 30)], 10, vel=4, vida=18, tam=6)

    def _picada(self, jugador):
        izq, der = self._limites()
        px = jugador.rect.centerx
        if self.fase == 0:
            meta_x = max(izq, min(der, px - DRAGON_W / 2))
            self.x += max(-5, min(5, meta_x - self.x))
            self.y += (40 - self.y) * 0.12
            if self.t_estado >= 40:
                dx, dy = px - DRAGON_W / 2 - self.x, SUELO - DRAGON_H + 4 - self.y
                d = math.hypot(dx, dy) or 1
                self.destino = (dx / d * 11, dy / d * 11)
                self.fase = 1
                self.t_estado = 0
        elif self.fase == 1:
            self.x += self.destino[0]
            self.y += self.destino[1]
            self.x = max(izq, min(der, self.x))
            if self.y >= SUELO - DRAGON_H or self.t_estado > 70:
                self.y = min(self.y, SUELO - DRAGON_H)
                if self.part: self.part.emitir(self.rect.midbottom[0], self.rect.midbottom[1], [(150, 130, 100), (190, 170, 130)], 14, vel=4, vida=25, tam=7, gravedad=0.1)
                self.sacudir = 12
                self.fase = 2
                self.t_estado = 0
        else:
            self.y += (ALTURA_VUELO - self.y) * 0.07
            if self.t_estado >= 50:
                self.estado = "combate"
                self.timer_picada = random.randint(360, 520)
                self.timer_disparo = 70

    def _caida(self):
        self.vy += 0.6
        self.y += self.vy
        if self.t % 2 == 0 and self.part: self.part.emitir(self.rect.center[0], self.rect.center[1], [(255, 120, 30), (90, 90, 90)], 2, vel=2, vida=25, tam=7)
        if self.y >= SUELO - DRAGON_H:
            self.y = SUELO - DRAGON_H
            if self.part: self.part.emitir(self.rect.center[0], self.rect.center[1], [(255, 200, 60), (255, 120, 30), (200, 40, 20), (80, 80, 80)], 60, vel=7, vida=50, tam=9, gravedad=0.1)
            self.sacudir = 30
            self.estado = "cenizas"
            self.t_estado = 0
            self.recien_derrotado = True

    def _cenizas(self):
        self.alpha = max(0, 255 - int(self.t_estado * 255 / 90))
        if self.t_estado % 5 == 0 and self.part: self.part.emitir(self.rect.center[0] + random.randint(-60, 60), self.rect.center[1], [(120, 120, 120), (80, 80, 80)], 2, vel=0.8, vida=40, tam=7, gravedad=-0.05)
        if self.t_estado >= 90: self.estado = "muerto"

    def _ala(self, lienzo, px, py, theta, largo, d, color):
        def punto(ang, k):
            a = math.radians(ang)
            return (px + d * largo * k * math.cos(a), py - largo * k * math.sin(a))

        punta = punto(theta, 1.0)
        m1 = punto(theta - 28, 0.82)
        m2 = punto(theta - 56, 0.64)
        base = punto(theta - 88, 0.38)
        pts = [(px, py), punta, m1, m2, base]
        pygame.draw.polygon(lienzo, color, pts)
        pygame.draw.polygon(lienzo, BORDE_ALA, pts, 3)
        pygame.draw.line(lienzo, BORDE_ALA, (px, py), punta, 4)
        pygame.draw.line(lienzo, BORDE_ALA, (px, py), m1, 2)
        pygame.draw.line(lienzo, BORDE_ALA, (px, py), m2, 2)

    def _cola(self, lienzo, bx, by, d):
        px, py = bx, by
        for k in range(9):
            px = bx + d * k * 14
            py = by + math.sin(self.t * 0.12 - k * 0.6) * (2 + k * 1.6) - k * 1.2
            r = max(3, 11 - k)
            pygame.draw.circle(lienzo, (120, 20, 35), (int(px), int(py)), r)
            pygame.draw.circle(lienzo, (190, 40, 50), (int(px), int(py - 1)), max(2, r - 3))
        pygame.draw.polygon(lienzo, (240, 130, 30), [(px, py - 8), (px + d * 20, py), (px, py + 8)])

    def _dibujar_cuerpo(self, pantalla, sx, sy):
        izq = self.mirando_izq
        d = 1 if izq else -1
        lienzo = pygame.Surface((DRAGON_W + 2 * MX, DRAGON_H + MY + 30), pygame.SRCALPHA)
        ox, oy = MX, MY
        ala_x = ox + (11.5 * E if izq else DRAGON_W - 11.5 * E)
        ala2_x = ox + (9.7 * E if izq else DRAGON_W - 9.7 * E)
        cola_x = ox + (21 * E if izq else DRAGON_W - 21 * E)
        ala_y, cola_y = oy + 3 * E, oy + 5.5 * E

        if self.estado == "dormido": theta, largo = 8, 70
        elif self.estado == "despertando":
            k = min(1.0, self.t_estado / 80)
            theta, largo = 8 + 60 * k + math.sin(self.t_estado * 0.3) * 10 * k, 70 + 40 * k
        elif self.estado in ("caida", "cenizas"): theta, largo = -40, 70
        elif self.estado == "picada" and self.fase == 1: theta, largo = -12, 110
        else: theta, largo = 22 + 52 * math.sin(self.t * 0.16), 110

        self._cola(lienzo, cola_x, cola_y, d)
        self._ala(lienzo, ala2_x, ala_y + 3, theta - 10, largo * 0.9, d, COLOR_ALA_FONDO)
        lienzo.blit(SPRITE_DRAGON if izq else SPRITE_DRAGON_DER, (ox, oy))
        self._ala(lienzo, ala_x, ala_y, theta, largo, d, COLOR_ALA)

        if self.flash > 0: lienzo.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGB_ADD)
        if self.alpha < 255: lienzo.set_alpha(self.alpha)
        pantalla.blit(lienzo, (sx - ox, sy - oy))

    def dibujar(self, pantalla, cam_x):
        if self.estado != "muerto":
            sx, sy = int(self.x - cam_x), int(self.y)
            if -400 < sx < ANCHO + 300:
                self._dibujar_cuerpo(pantalla, sx, sy)
                if self.estado == "cargando":
                    bx, by = self.boca()
                    k = 1 - self.cargando / 28
                    r = int(6 + 18 * k)
                    c = (int(bx - cam_x), int(by))
                    pygame.draw.circle(pantalla, (255, 120, 30), c, r + 4)
                    pygame.draw.circle(pantalla, (255, 220, 90), c, r)
                if self.estado != "cenizas":
                    cx = sx + DRAGON_W // 2
                    ty = max(6, sy - 70)
                    tx = cx - TEXTO_BOSS.get_width() // 2
                    for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1)): pantalla.blit(SOMBRA_BOSS, (tx + ddx, ty + ddy))
                    pantalla.blit(TEXTO_BOSS, (tx, ty))
                    ancho = 80
                    bx0 = cx - ancho // 2
                    pygame.draw.rect(pantalla, (40, 10, 15), (bx0, ty + 17, ancho, 5))
                    pygame.draw.rect(pantalla, (225, 30, 30), (bx0, ty + 17, ancho * self.hp / DRAGON_HP, 5))
        for b in self.bolas: b.dibujar(pantalla, cam_x)