import math, random, pygame
from config import *


# ---------- Cámara ----------
class Camara:
    def __init__(self):
        self.x = 0.0
        self.ox = 0
        self.temblor = 0

    def _meta(self, objetivo_x):
        return max(0, min(objetivo_x - ANCHO / 2, MAPA_LARGO - ANCHO))

    def ir_a(self, objetivo_x):
        self.x = self._meta(objetivo_x)
        self.ox = int(self.x)

    def seguir(self, objetivo_x):
        self.x += (self._meta(objetivo_x) - self.x) * 0.12
        self.ox = int(self.x)
        if self.temblor > 0:
            self.ox += random.randint(-self.temblor, self.temblor) // 2
            self.temblor -= 1


# ---------- Colores del suelo ----------
PALETA_SUELO = [
    (90, 170, 80), (110, 178, 72), (150, 175, 70), (180, 150, 70),
    (160, 120, 80), (130, 115, 95), (115, 105, 100), (105, 100, 105),
]


def _mezclar(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def color_suelo(x):
    pos = max(0, min(x / ZONA_PX, len(PALETA_SUELO) - 1.001))
    i = int(pos)
    return _mezclar(PALETA_SUELO[i], PALETA_SUELO[i + 1], pos - i)


BRILLO = pygame.Surface((120, 120), pygame.SRCALPHA)
for _r in range(60, 0, -6):
    pygame.draw.circle(BRILLO, (255, 160, 60, int(6 + (60 - _r))), (60, 60), _r)


# ---------- Cielo y paisaje ----------
NUBES = [(100, 70, 1.0), (520, 120, 0.7), (900, 50, 1.2), (1300, 100, 0.8)]
PERIODO_NUBES = 1700
COLINAS = [(150, 260, 110), (520, 340, 160), (900, 300, 90)]
PERIODO_COLINAS = 1200


def _nube(pantalla, x, y, e):
    for dx, dy, r in ((0, 0, 28), (30, -12, 34), (64, 0, 28), (32, 8, 26)):
        pygame.draw.circle(pantalla, (255, 255, 255),
                           (int(x + dx * e), int(y + dy * e)), int(r * e))


def dibujar_nubes(pantalla, cam_x):
    for ox, y, esc in NUBES:
        sx = (ox - cam_x * 0.2) % PERIODO_NUBES - 150
        _nube(pantalla, sx, y, esc)


def dibujar_colinas(pantalla, cam_x, base):
    color = tuple(int(c * 0.75) for c in base)
    for ox, w, h in COLINAS:
        sx = (ox - cam_x * 0.4) % PERIODO_COLINAS - 200
        pygame.draw.ellipse(pantalla, color,
                            (int(sx - w // 2), SUELO - h, w, h * 2))


def dibujar_suelo(pantalla, cam_x, color):
    oscuro = tuple(int(c * 0.72) for c in color)
    pygame.draw.rect(pantalla, color, (0, SUELO, ANCHO, ALTO - SUELO))
    pygame.draw.rect(pantalla, oscuro, (0, SUELO, ANCHO, 6))
    paso = 70
    primero = int(cam_x // paso)
    for i in range(primero, primero + ANCHO // paso + 2):
        if (i * 37) % 5 < 3:
            x = i * paso + (i * 53) % 40 - cam_x
            y = SUELO + 14 + (i * 29) % 70
            pygame.draw.line(pantalla, oscuro, (x, y), (x - 4, y - 8), 2)
            pygame.draw.line(pantalla, oscuro, (x, y), (x + 4, y - 8), 2)


def dibujar_arboles(pantalla, cam_x, color):
    hoja = tuple(int(c * 0.8) for c in color)
    paso = 330
    primero = int(cam_x // paso) - 1
    for i in range(primero, primero + ANCHO // paso + 4):
        mundo_x = i * paso + (i * 71) % 120
        if mundo_x < 200 or mundo_x > CASTILLO_X - 250:
            continue
        # Evitar árboles sobre la casa y la herrería
        if CASA_X - 120 < mundo_x < CASA_X + CASA_ANCHO + 120:
            continue
        if HERRERIA_X - 120 < mundo_x < HERRERIA_X + HERRERIA_ANCHO + 120:
            continue
        if (i * 13) % 4 == 0:
            continue
        x = mundo_x - cam_x
        alto = 70 + (i * 29) % 50
        pygame.draw.rect(pantalla, (95, 65, 40), (x - 7, SUELO - alto, 14, alto))
        pygame.draw.circle(pantalla, hoja, (x, SUELO - alto - 10), 38)
        pygame.draw.circle(pantalla, hoja, (x - 26, SUELO - alto + 8), 28)
        pygame.draw.circle(pantalla, hoja, (x + 26, SUELO - alto + 8), 28)


# ---------- Casa de Aventura ----------
def dibujar_casa(pantalla, cam_x, jugador_cerca_puerta=False):
    t = pygame.time.get_ticks()
    x0 = CASA_X - cam_x
    x1 = x0 + CASA_ANCHO
    if x1 < -200 or x0 > ANCHO + 200:
        return

    madera = (140, 95, 60)
    madera_osc = (95, 60, 35)
    linea = (70, 45, 25)
    techo = (170, 50, 50)
    techo_osc = (120, 30, 30)

    base_y = SUELO
    alto_pared = 180
    pared_y = base_y - alto_pared

    pygame.draw.rect(pantalla, madera, (x0, pared_y, CASA_ANCHO, alto_pared))
    for tx in range(x0, x1, 32):
        pygame.draw.line(pantalla, madera_osc, (tx, pared_y), (tx, base_y), 2)
    pygame.draw.rect(pantalla, linea, (x0, pared_y, CASA_ANCHO, alto_pared), 3)

    pygame.draw.polygon(pantalla, techo, [
        (x0 - 30, pared_y),
        (x0 + CASA_ANCHO // 2, pared_y - 110),
        (x1 + 30, pared_y)])
    pygame.draw.polygon(pantalla, techo_osc, [
        (x0 - 30, pared_y),
        (x0 + CASA_ANCHO // 2, pared_y - 110),
        (x1 + 30, pared_y)], 3)
    for i in range(1, 5):
        k = i / 5
        mx = x0 + CASA_ANCHO // 2
        top = pared_y - 110
        pygame.draw.line(pantalla, techo_osc,
                         (mx - (mx - (x0 - 30)) * k, top + 110 * k),
                         (mx + ((x1 + 30) - mx) * k, top + 110 * k), 2)

    ch_x = x1 - 80
    ch_y = pared_y - 130
    pygame.draw.rect(pantalla, madera_osc, (ch_x, ch_y, 26, 60))
    pygame.draw.rect(pantalla, linea, (ch_x, ch_y, 26, 60), 2)
    for i in range(3):
        fase = (t / 30 + i * 40) % 120
        hy = ch_y - fase * 0.5
        hx = ch_x + 13 + math.sin((t / 200) + i) * 8
        radio = max(2, int(12 - fase / 12))
        alpha = int(140 - fase)
        if alpha > 0:
            humo = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(humo, (200, 200, 200, alpha),
                               (radio, radio), radio)
            pantalla.blit(humo, (hx - radio, hy - radio))

    for wx in (x0 + 60, x1 - 130):
        pygame.draw.rect(pantalla, (255, 220, 130), (wx, pared_y + 40, 70, 60))
        pygame.draw.rect(pantalla, linea, (wx, pared_y + 40, 70, 60), 3)
        pygame.draw.line(pantalla, linea,
                         (wx + 35, pared_y + 40), (wx + 35, pared_y + 100), 2)
        pygame.draw.line(pantalla, linea,
                         (wx, pared_y + 70), (wx + 70, pared_y + 70), 2)

    px = CASA_PUERTA_X - cam_x
    py = SUELO - CASA_PUERTA_ALTO
    pw = CASA_PUERTA_ANCHO
    ph = CASA_PUERTA_ALTO

    pygame.draw.rect(pantalla, madera_osc, (px - 8, py - 6, pw + 16, ph + 6),
                     border_top_left_radius=pw // 2 + 8,
                     border_top_right_radius=pw // 2 + 8)
    pygame.draw.rect(pantalla, (70, 45, 25), (px, py, pw, ph),
                     border_top_left_radius=pw // 2,
                     border_top_right_radius=pw // 2)
    pygame.draw.line(pantalla, linea,
                     (px + pw // 2, py + 8), (px + pw // 2, py + ph), 2)
    pygame.draw.circle(pantalla, (220, 200, 80), (px + pw - 14, py + ph // 2), 4)

    pygame.font.init()
    f = pygame.font.SysFont(None, 28)
    txt = f.render("Aventura", True, (255, 240, 200))
    sombra = f.render("Aventura", True, (0, 0, 0))
    letrero_w = txt.get_width() + 30
    letrero_h = txt.get_height() + 14
    lx = x0 + CASA_ANCHO // 2 - letrero_w // 2
    ly = pared_y - 40
    pygame.draw.line(pantalla, linea, (x0 + 20, ly), (lx, ly + 6), 2)
    pygame.draw.line(pantalla, linea, (x1 - 20, ly), (lx + letrero_w, ly + 6), 2)
    pygame.draw.rect(pantalla, (110, 70, 40), (lx, ly, letrero_w, letrero_h),
                     border_radius=4)
    pygame.draw.rect(pantalla, linea, (lx, ly, letrero_w, letrero_h), 2, border_radius=4)
    pantalla.blit(sombra, (lx + 16, ly + 8))
    pantalla.blit(txt, (lx + 15, ly + 7))

    if jugador_cerca_puerta:
        pulso = int(30 + 20 * math.sin(t / 150))
        brillo_surf = pygame.Surface((pw + 60, ph + 60), pygame.SRCALPHA)
        pygame.draw.rect(brillo_surf, (255, 240, 150, pulso),
                         brillo_surf.get_rect(), border_radius=30)
        pantalla.blit(brillo_surf, (px - 30, py - 30))
        f2 = pygame.font.SysFont(None, 26)
        txt2 = f2.render("W: Entrar", True, (255, 240, 150))
        sombra2 = f2.render("W: Entrar", True, (0, 0, 0))
        tx = px + pw // 2 - txt2.get_width() // 2
        ty = py - 50 + int(math.sin(t / 200) * 4)
        pantalla.blit(sombra2, (tx + 1, ty + 1))
        pantalla.blit(txt2, (tx, ty))


# ---------- Herrería ----------
def dibujar_herreria(pantalla, cam_x, jugador_cerca_puerta=False):
    t = pygame.time.get_ticks()
    x0 = HERRERIA_X - cam_x
    x1 = x0 + HERRERIA_ANCHO
    if x1 < -200 or x0 > ANCHO + 200:
        return

    piedra = (90, 85, 95)
    piedra_osc = (60, 55, 65)
    linea = (40, 35, 45)
    techo = (60, 60, 70)
    techo_osc = (35, 35, 45)

    base_y = SUELO
    alto_pared = 190
    pared_y = base_y - alto_pared

    pygame.draw.rect(pantalla, piedra, (x0, pared_y, HERRERIA_ANCHO, alto_pared))
    for fila, yy in enumerate(range(pared_y, base_y, 28)):
        pygame.draw.line(pantalla, linea, (x0, yy), (x1, yy), 2)
        off = 28 if fila % 2 else 0
        for xx in range(x0 + off, x1, 56):
            pygame.draw.line(pantalla, linea, (xx, yy),
                             (xx, min(yy + 28, base_y)), 2)
    pygame.draw.rect(pantalla, linea, (x0, pared_y, HERRERIA_ANCHO, alto_pared), 3)

    # Techo plano de losas
    pygame.draw.rect(pantalla, techo, (x0 - 20, pared_y - 30, HERRERIA_ANCHO + 40, 30))
    pygame.draw.rect(pantalla, techo_osc, (x0 - 20, pared_y - 30, HERRERIA_ANCHO + 40, 30), 3)
    for lx in range(int(x0 - 20), int(x1 + 20), 40):
        pygame.draw.line(pantalla, techo_osc, (lx, pared_y - 30), (lx, pared_y), 2)

    # Chimenea alta con fuego
    ch_x = x1 - 90
    ch_y = pared_y - 120
    pygame.draw.rect(pantalla, piedra_osc, (ch_x, ch_y, 40, 120))
    pygame.draw.rect(pantalla, linea, (ch_x, ch_y, 40, 120), 3)
    # Fuego
    parp = math.sin(t / 80) * 4
    pygame.draw.polygon(pantalla, (240, 110, 20), [
        (ch_x + 8, ch_y + 10), (ch_x + 20, ch_y - 15 - parp), (ch_x + 32, ch_y + 10)])
    pygame.draw.polygon(pantalla, (255, 220, 90), [
        (ch_x + 13, ch_y + 10), (ch_x + 20, ch_y - 5 - parp), (ch_x + 27, ch_y + 10)])

    # Ventanas pequeñas
    for wx in (x0 + 60, x1 - 130):
        pygame.draw.rect(pantalla, (255, 160, 60), (wx, pared_y + 50, 50, 40))
        pygame.draw.rect(pantalla, linea, (wx, pared_y + 50, 50, 40), 3)
        pygame.draw.line(pantalla, linea, (wx + 25, pared_y + 50),
                         (wx + 25, pared_y + 90), 2)

    # Puerta
    px = HERRERIA_PUERTA_X - cam_x
    py = SUELO - HERRERIA_PUERTA_ALTO
    pw = HERRERIA_PUERTA_ANCHO
    ph = HERRERIA_PUERTA_ALTO

    pygame.draw.rect(pantalla, piedra_osc, (px - 8, py - 6, pw + 16, ph + 6),
                     border_top_left_radius=pw // 2 + 8,
                     border_top_right_radius=pw // 2 + 8)
    pygame.draw.rect(pantalla, (45, 40, 50), (px, py, pw, ph),
                     border_top_left_radius=pw // 2,
                     border_top_right_radius=pw // 2)
    # Remaches
    for i in range(1, 4):
        ry = py + i * ph // 4
        pygame.draw.circle(pantalla, (140, 140, 150), (px + 10, ry), 3)
        pygame.draw.circle(pantalla, (140, 140, 150), (px + pw - 10, ry), 3)

    # Letrero "Herrería"
    pygame.font.init()
    f = pygame.font.SysFont(None, 28)
    txt = f.render("Herreria", True, (255, 220, 180))
    sombra = f.render("Herreria", True, (0, 0, 0))
    letrero_w = txt.get_width() + 30
    letrero_h = txt.get_height() + 14
    lx = x0 + HERRERIA_ANCHO // 2 - letrero_w // 2
    ly = pared_y - 40
    pygame.draw.line(pantalla, linea, (x0 + 20, ly), (lx, ly + 6), 2)
    pygame.draw.line(pantalla, linea, (x1 - 20, ly), (lx + letrero_w, ly + 6), 2)
    pygame.draw.rect(pantalla, (60, 45, 40), (lx, ly, letrero_w, letrero_h),
                     border_radius=4)
    pygame.draw.rect(pantalla, linea, (lx, ly, letrero_w, letrero_h), 2, border_radius=4)
    pantalla.blit(sombra, (lx + 16, ly + 8))
    pantalla.blit(txt, (lx + 15, ly + 7))

    if jugador_cerca_puerta:
        pulso = int(30 + 20 * math.sin(t / 150))
        brillo_surf = pygame.Surface((pw + 60, ph + 60), pygame.SRCALPHA)
        pygame.draw.rect(brillo_surf, (255, 240, 150, pulso),
                         brillo_surf.get_rect(), border_radius=30)
        pantalla.blit(brillo_surf, (px - 30, py - 30))
        f2 = pygame.font.SysFont(None, 26)
        txt2 = f2.render("W: Entrar", True, (255, 240, 150))
        sombra2 = f2.render("W: Entrar", True, (0, 0, 0))
        tx = px + pw // 2 - txt2.get_width() // 2
        ty = py - 50 + int(math.sin(t / 200) * 4)
        pantalla.blit(sombra2, (tx + 1, ty + 1))
        pantalla.blit(txt2, (tx, ty))


# ---------- Castillo ----------
def _ladrillos(pantalla, x, y, w, h, color, linea):
    pygame.draw.rect(pantalla, color, (x, y, w, h))
    for fila, yy in enumerate(range(y, y + h, 24)):
        pygame.draw.line(pantalla, linea, (x, yy), (x + w, yy), 2)
        desfase = 24 if fila % 2 else 0
        for xx in range(x + desfase, x + w, 48):
            pygame.draw.line(pantalla, linea, (xx, yy),
                             (xx, min(yy + 24, y + h)), 2)


def _almenas(pantalla, x, y, w, color, linea, alto=22, ancho=28, espacio=44):
    for xx in range(x, x + w, espacio):
        pygame.draw.rect(pantalla, color, (xx, y - alto, ancho, alto))
        pygame.draw.rect(pantalla, linea, (xx, y - alto, ancho, alto), 2)


def _antorcha(pantalla, x, y, t, fase):
    parpadeo = math.sin(t / 90 + fase * 1.7) * 3
    pantalla.blit(BRILLO, (x - 60, y - 20 - 60))
    pygame.draw.rect(pantalla, (60, 40, 30), (x - 4, y, 8, 34))
    pygame.draw.rect(pantalla, (90, 90, 100), (x - 9, y - 4, 18, 8))
    pygame.draw.polygon(pantalla, (240, 110, 20),
                        [(x - 9, y - 4), (x, y - 32 - parpadeo * 2), (x + 9, y - 4)])
    pygame.draw.polygon(pantalla, (255, 220, 90),
                        [(x - 5, y - 4), (x, y - 22 - parpadeo), (x + 5, y - 4)])


def dibujar_castillo(pantalla, cam_x, jugador_cerca_puerta=False):
    t = pygame.time.get_ticks()
    x0 = CASTILLO_X - cam_x
    x1 = x0 + CASTILLO_ANCHO
    if x1 < -200 or x0 > ANCHO + 200:
        return

    piedra = (100, 100, 115)
    piedra_oscura = (70, 70, 85)
    linea = (50, 50, 65)
    techo = (140, 40, 50)
    techo_osc = (100, 25, 35)

    altura_muro = 260
    muro_y = SUELO - altura_muro
    _ladrillos(pantalla, x0 + 120, muro_y, CASTILLO_ANCHO - 240,
               altura_muro, piedra, linea)
    _almenas(pantalla, x0 + 120, muro_y, CASTILLO_ANCHO - 240, piedra, linea)

    torre_w = 140
    torre_alto = 360
    torre_y = SUELO - torre_alto

    for tx in (x0 + 20, x1 - 20 - torre_w):
        _ladrillos(pantalla, tx, torre_y, torre_w, torre_alto, piedra, linea)
        _almenas(pantalla, tx, torre_y, torre_w, piedra, linea,
                 alto=26, ancho=30, espacio=46)
        pygame.draw.polygon(pantalla, techo, [
            (tx - 10, torre_y - 20),
            (tx + torre_w // 2, torre_y - 100),
            (tx + torre_w + 10, torre_y - 20)])
        pygame.draw.polygon(pantalla, techo_osc, [
            (tx - 10, torre_y - 20),
            (tx + torre_w // 2, torre_y - 100),
            (tx + torre_w + 10, torre_y - 20)], 3)
        vx = tx + torre_w // 2
        pygame.draw.rect(pantalla, (25, 20, 35), (vx - 12, torre_y + 80, 24, 40),
                         border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.rect(pantalla, (25, 20, 35), (vx - 12, torre_y + 150, 24, 40),
                         border_top_left_radius=12, border_top_right_radius=12)

    px = PUERTA_X - cam_x
    py = SUELO - PUERTA_ALTO
    pw = PUERTA_ANCHO
    ph = PUERTA_ALTO

    pygame.draw.rect(pantalla, piedra_oscura, (px - 14, py - 10, pw + 28, ph + 10),
                     border_top_left_radius=pw // 2 + 14,
                     border_top_right_radius=pw // 2 + 14)
    pygame.draw.rect(pantalla, (70, 45, 25), (px, py, pw, ph),
                     border_top_left_radius=pw // 2,
                     border_top_right_radius=pw // 2)
    for i in range(1, 5):
        ly = py + i * ph // 5
        pygame.draw.line(pantalla, (50, 30, 15), (px + 6, ly), (px + pw - 6, ly), 2)
    pygame.draw.line(pantalla, (50, 30, 15),
                     (px + pw // 2, py + 10), (px + pw // 2, py + ph), 2)
    for fy in (py + ph // 3, py + 2 * ph // 3):
        pygame.draw.circle(pantalla, (40, 40, 50), (px + 18, fy), 5)
        pygame.draw.circle(pantalla, (40, 40, 50), (px + pw - 18, fy), 5)

    if jugador_cerca_puerta:
        pulso = int(30 + 20 * math.sin(t / 150))
        brillo_surf = pygame.Surface((pw + 60, ph + 60), pygame.SRCALPHA)
        pygame.draw.rect(brillo_surf, (255, 240, 150, pulso),
                         brillo_surf.get_rect(), border_radius=30)
        pantalla.blit(brillo_surf, (px - 30, py - 30))
        f = pygame.font.SysFont(None, 26)
        txt = f.render("W: Entrar", True, (255, 240, 150))
        sombra = f.render("W: Entrar", True, (0, 0, 0))
        tx = px + pw // 2 - txt.get_width() // 2
        ty = py - 50 + int(math.sin(t / 200) * 4)
        pantalla.blit(sombra, (tx + 1, ty + 1))
        pantalla.blit(txt, (tx, ty))

    for n, ax in enumerate((px - 80, px + pw + 80)):
        _antorcha(pantalla, ax, SUELO - 180, t, n)

    for ex in (x0 + 300, x1 - 300):
        mov = int(math.sin(t / 400) * 3)
        pygame.draw.polygon(pantalla, (170, 30, 40), [
            (ex - 18, muro_y + 30), (ex + 18, muro_y + 30),
            (ex + 18 + mov, muro_y + 110), (ex + mov, muro_y + 96),
            (ex - 18 + mov, muro_y + 110)])
        pygame.draw.polygon(pantalla, (240, 200, 40), [
            (ex - 18, muro_y + 30), (ex + 18, muro_y + 30),
            (ex + 18 + mov, muro_y + 110), (ex + mov, muro_y + 96),
            (ex - 18 + mov, muro_y + 110)], 2)


def dibujar_fondo(pantalla, cam_x, cerca_puerta_castillo=False,
                  cerca_puerta_casa=False, cerca_puerta_herreria=False):
    suelo = color_suelo(cam_x + ANCHO // 2)
    pantalla.fill((135, 206, 235))
    pygame.draw.circle(pantalla, (255, 240, 170), (680, 80), 52)
    pygame.draw.circle(pantalla, (255, 220, 60), (680, 80), 38)
    dibujar_nubes(pantalla, cam_x)
    dibujar_colinas(pantalla, cam_x, suelo)
    dibujar_suelo(pantalla, cam_x, suelo)
    dibujar_arboles(pantalla, cam_x, suelo)
    dibujar_casa(pantalla, cam_x, cerca_puerta_casa)
    dibujar_herreria(pantalla, cam_x, cerca_puerta_herreria)
    dibujar_castillo(pantalla, cam_x, cerca_puerta_castillo)