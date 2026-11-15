import math, random, pygame
from config import *
from sprites import (SPRITE_HEROE_1, SPRITE_HEROE_2,
                     SPRITE_HEROE_1_IZQ, SPRITE_HEROE_2_IZQ,
                     SPRITE_ESPADA, SPRITE_ARMADURA, SPRITE_ARMADURA_IZQ)

class ProyectilFuego:
    def __init__(self, x, y, vx, vy, dano, tipo="dragon"):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.dano = dano
        self.tipo = tipo
        self.radio = 14 if tipo == "demonio" else 12
        self.vida = DEMONIO_BOLA_VIDA if tipo == "demonio" else DRAGON_BOLA_VIDA
        self.viva = True
        self.t = 0

    @property
    def rect(self):
        r = self.radio
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def actualizar(self, objetivos, particulas):
        self.t += 1
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

        if particulas:
            colores = [(180, 30, 255), (100, 0, 150), (255, 100, 255)] if self.tipo == "demonio" else [(255, 200, 60), (255, 120, 30), (200, 50, 20)]
            particulas.emitir(self.x, self.y, colores, 2, vel=1.5, vida=20, tam=6, gravedad=-0.05)

        for obj in objetivos:
            if self.rect.colliderect(obj.rect):
                obj.recibir_golpe(self.dano, 40 if self.vx > 0 else -40)
                self.explotar(particulas)
                return

        if (self.vida <= 0 or self.y >= SUELO - 6 or self.x < -100 or self.x > MAPA_LARGO + 100):
            self.explotar(particulas)

    def explotar(self, particulas):
        if particulas:
            colores = [(255, 0, 200), (200, 0, 100), (100, 0, 50)] if self.tipo == "demonio" else [(255, 220, 90), (255, 130, 30), (200, 50, 20)]
            particulas.emitir(self.x, self.y, colores, 20, vel=6, vida=30, tam=8, gravedad=0.1)
        self.viva = False

    def dibujar(self, pantalla, cam_x):
        sx, sy = int(self.x - cam_x), int(self.y)
        if sx < -50 or sx > ANCHO + 50: return
        r = self.radio + int(math.sin(self.t / 5) * 2)
        
        if self.tipo == "demonio":
            pygame.draw.circle(pantalla, (60, 0, 90), (sx, sy), r + 5)
            pygame.draw.circle(pantalla, (150, 30, 200), (sx, sy), r)
            pygame.draw.circle(pantalla, (255, 150, 255), (sx, sy), max(2, r // 2))
            pygame.draw.circle(pantalla, (255, 255, 255), (sx, sy), max(1, r // 4))
        else:
            pygame.draw.circle(pantalla, (200, 50, 20), (sx, sy), r + 5)
            pygame.draw.circle(pantalla, (255, 140, 30), (sx, sy), r)
            pygame.draw.circle(pantalla, (255, 230, 120), (sx, sy), max(2, r // 2))


class Jugador:
    def __init__(self, base, datos, inventario=None, particulas=None):
        self.base = base
        self.datos = datos
        self.inventario = inventario
        self.particulas = particulas
        self.rect = pygame.Rect(150, SUELO - 70, 50, 70)
        self.vy = 0.0
        self.en_suelo = True
        self.mirando_derecha = True

        self.espada_equipada = False
        self.armadura_equipada = False

        self.ataque_cd = 0
        self.golpe_t = 0
        self.golpe_aplicado = False
        self.dir_golpe = True
        self.invulnerable = 0
        self.punto_reaparicion = 150
        self.limite_x = MAPA_LARGO

        self.z_cd = 0
        self.z_anim_t = 0
        self.z_x = 0
        self.z_y = 0

        self.anim_t = 0
        self.frame = 0
        self.aura_t = 0

        # --- Kitsune ---
        self.trans_activa = False
        self.trans_cd = 0
        self.cola_t = 0
        self.trans_anim_t = 0
        self.trans_anim_tipo = ""
        self.pulso_aura = 0.0
        self.huellas = []
        self.huella_timer = 0
        self.huella_paso = 0

        # --- Dragón ---
        self.dragon_trans = False
        self.dragon_trans_cd = 0
        self.dragon_anim_t = 0
        self.dragon_anim_tipo = ""
        self.dragon_ala_t = 0
        self.dragon_aliento_cd = 0
        self.bolas_fuego = []
        self.volando = False
        self.dragon_aura_pulso = 0.0

        # --- Demonio ---
        self.demonio_trans = False
        self.demonio_trans_cd = 0
        self.demonio_anim_t = 0
        self.demonio_anim_tipo = ""
        self.demonio_bola_cd = 0
        self.bolas_infernales = []
        self.demonio_aura_pulso = 0.0

        self.vida = self.vida_max

    def _es_kitsune(self): return self.datos.get("raza") == "kitsune"
    def _es_dragon(self): return self.datos.get("raza") == "dragon"
    def _es_demonio(self): return self.datos.get("raza") == "demonio"

    @property
    def dano(self):
        base = self.base["daño"] + COMBATE_DANO_POR_PUNTO * self.datos["combate"]
        if self.espada_equipada: base += ESPADA_INFER_DANO_EXTRA
        raza = self.datos.get("raza", "humano")
        
        if raza == "dragon": base = int(base * 1.15)
        elif raza == "demonio": base = int(base * 1.25)
        elif raza == "elfo": base = int(base * 1.10)
        
        if self.trans_activa: base = int(base * KITSUNE_TRANS_DANO)
        if self.dragon_trans: base = int(base * DRAGON_TRANS_DANO)
        if self.demonio_trans: base = int(base * DEMONIO_TRANS_DANO)
        return base

    @property
    def vida_max(self):
        base = self.base["vida"] + VIDA_POR_PUNTO * self.datos["vida"]
        if self.armadura_equipada: base += ARMADURA_INFER_VIDA_EXTRA
        raza = self.datos.get("raza", "humano")
        
        if raza == "humano": base += 20
        elif raza == "demonio": base = int(base * 1.15)
        
        if self.dragon_trans: base = int(base * DRAGON_TRANS_VIDA)
        if self.demonio_trans: base = int(base * DEMONIO_TRANS_VIDA)
        return base

    @property
    def velocidad(self):
        base = self.base["velocidad"]
        raza = self.datos.get("raza", "humano")
        
        if raza == "bestia": base = int(base * 1.10)
        elif raza == "kitsune": base = int(base * KITSUNE_VEL_BONUS)
        elif raza == "dragon": base = int(base * DRAGON_VEL_BONUS)
        elif raza == "hada": base = int(base * 1.15)
        elif raza == "elfo": base = int(base * 1.05)
        elif raza == "lobo": base = int(base * 1.15)
        elif raza == "ave": base = int(base * 1.20)
        
        if self.trans_activa: base = int(base * KITSUNE_TRANS_VEL)
        if self.dragon_trans: base = int(base * DRAGON_TRANS_VEL)
        if self.demonio_trans: base = int(base * DEMONIO_TRANS_VEL)
        return base

    @property
    def cooldown(self):
        cd = max(DURACION_GOLPE, 30 - COMBATE_VELOCIDAD_POR_PUNTO * self.datos["combate"])
        if self.demonio_trans: cd = max(DURACION_GOLPE, int(cd * 0.75))
        return cd

    @property
    def dano_z(self):
        return Z_DANO + (PODER_DANO_HABILIDAD * self.datos["poder"])

    def saltar(self):
        if self.dragon_trans: return
        if self.en_suelo:
            self.vy = SALTO
            self.en_suelo = False
            if self.particulas: self.particulas.emitir_polvo(self.rect.centerx, self.rect.bottom, 5)

    def recibir_dano(self, cantidad):
        if self.invulnerable > 0: return
        raza = self.datos.get("raza", "humano")

        if raza == "sombra" and random.random() < 0.15:
            self.invulnerable = 20
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(80, 80, 80), (40, 40, 40)], 10, vel=4, vida=20)
            return

        if raza == "kitsune" and random.random() < KITSUNE_ESQUIVA:
            self.invulnerable = 20
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(240, 160, 60), (255, 200, 100)], 12, vel=5, vida=20)
            return

        if self.armadura_equipada:
            cantidad = int(cantidad * 0.8)
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(200, 50, 50), (100, 0, 0)], 10, vel=3, vida=20)

        self.vida -= cantidad
        self.invulnerable = 40
        if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(255, 50, 50), (200, 0, 0)], 8, vel=4, vida=20)

    def revivir(self):
        self.vida = self.vida_max
        self.rect.x = self.punto_reaparicion
        self.vy = 0
        self.invulnerable = 60
        self.trans_activa = False
        self.dragon_trans = False
        self.demonio_trans = False
        self.trans_anim_t = 0
        self.dragon_anim_t = 0
        self.demonio_anim_t = 0
        self.huellas.clear()
        self.bolas_fuego.clear()
        self.bolas_infernales.clear()

    def teletransportar(self, x):
        self.rect.x = x
        self.vy = 0
        self.rect.bottom = SUELO
        self.en_suelo = True

    def cerca_de_puerta_exterior(self): return (PUERTA_X - 40 <= self.rect.centerx <= PUERTA_X + PUERTA_ANCHO + 40 and self.en_suelo)
    def cerca_de_puerta_interior(self): return self.rect.centerx <= 140 and self.en_suelo
    def cerca_de_puerta_casa(self): return (CASA_PUERTA_X - 40 <= self.rect.centerx <= CASA_PUERTA_X + CASA_PUERTA_ANCHO + 40 and self.en_suelo)
    def cerca_de_puerta_casa_interior(self): return self.rect.centerx <= 130 and self.en_suelo
    def cerca_de_puerta_herreria(self): return (HERRERIA_PUERTA_X - 40 <= self.rect.centerx <= HERRERIA_PUERTA_X + HERRERIA_PUERTA_ANCHO + 40 and self.en_suelo)
    def cerca_de_puerta_herreria_interior(self): return self.rect.centerx <= 130 and self.en_suelo

    def usar_item(self, item_id): return False

    def equipar_item(self, item_id):
        if item_id == "espada_infernal":
            self.espada_equipada = True
            return True
        elif item_id == "armadura_infernal":
            self.armadura_equipada = True
            self.vida += ARMADURA_INFER_VIDA_EXTRA
            return True
        return False

    def desequipar_item(self, item_id):
        if item_id == "armadura_infernal" and self.armadura_equipada:
            self.armadura_equipada = False
            self.vida = max(1, self.vida - ARMADURA_INFER_VIDA_EXTRA)
            return True
        return False

    def habilidad_z(self, objetivos):
        if self.espada_equipada and self.z_cd <= 0:
            self.z_cd = Z_COOLDOWN
            self.z_anim_t = 25
            self.z_x = self.rect.centerx
            self.z_y = self.rect.centery
            if self.particulas:
                self.particulas.emitir(self.z_x, self.z_y, [(255, 100, 0), (255, 200, 0), (200, 30, 0)], 50, vel=8, vida=35, tam=9)
            for obj in objetivos:
                dx = obj.rect.centerx - self.rect.centerx
                dy = obj.rect.centery - self.rect.centery
                if (dx * dx + dy * dy) ** 0.5 <= Z_RADIO:
                    obj.recibir_golpe(self.dano_z, 80 if dx > 0 else -80)

    def toggle_transformacion_kitsune(self):
        if not self._es_kitsune(): return None
        if self.trans_activa:
            self.trans_activa = False
            self.trans_cd = KITSUNE_TRANS_CD
            self.trans_anim_t = 20
            self.trans_anim_tipo = "off"
            self.huellas.clear()
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(255, 220, 120), (255, 180, 60), (255, 255, 200)], 50, vel=8, vida=35, tam=9)
            return "Transformación desactivada"
        if self.trans_cd > 0: return None
        self.trans_activa = True
        self.trans_anim_t = 25
        self.trans_anim_tipo = "on"
        if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(255, 140, 40), (255, 200, 80), (255, 240, 150)], 80, vel=10, vida=45, tam=10)
        return "¡TRANSFORMACIÓN KITSUNE!"

    def toggle_transformacion_dragon(self):
        if not self._es_dragon(): return None
        if self.dragon_trans:
            self.dragon_trans = False
            self.dragon_trans_cd = DRAGON_TRANS_CD
            self.dragon_anim_t = 22
            self.dragon_anim_tipo = "off"
            self.volando = False
            if self.rect.bottom < SUELO: self.vy = 8
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(255, 100, 30), (200, 50, 20), (255, 200, 80)], 60, vel=9, vida=40, tam=10)
            return "Dragón desactivado"
        if self.dragon_trans_cd > 0: return None
        self.dragon_trans = True
        self.dragon_anim_t = 28
        self.dragon_anim_tipo = "on"
        self.vy = -6
        if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(200, 40, 30), (255, 100, 30), (255, 200, 60)], 100, vel=12, vida=50, tam=11)
        return "¡TRANSFORMACIÓN DRAGÓN!"

    def toggle_transformacion_demonio(self):
        if not self._es_demonio(): return None
        if self.demonio_trans:
            self.demonio_trans = False
            self.demonio_trans_cd = DEMONIO_TRANS_CD
            self.demonio_anim_t = 22
            self.demonio_anim_tipo = "off"
            if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(150, 30, 200), (60, 0, 90)], 60, vel=9, vida=40, tam=10)
            return "Demonio desactivado"
        if self.demonio_trans_cd > 0: return None
        
        self.demonio_trans = True
        self.demonio_anim_t = 28
        self.demonio_anim_tipo = "on"
        if self.particulas: self.particulas.emitir(self.rect.centerx, self.rect.centery, [(150, 30, 200), (255, 50, 150), (60, 0, 90)], 80, vel=10, vida=50, tam=10)
        return "¡TRANSFORMACIÓN DEMONIO!"

    def lanzar_bola_infernal(self):
        if not self.demonio_trans or self.demonio_bola_cd > 0: return False
        self.demonio_bola_cd = DEMONIO_BOLA_CD
        bx = self.rect.right + 10 if self.mirando_derecha else self.rect.left - 10
        vx = DEMONIO_BOLA_VEL if self.mirando_derecha else -DEMONIO_BOLA_VEL
        by = self.rect.centery - 5
        self.bolas_infernales.append(ProyectilFuego(bx, by, vx, -1.0, DEMONIO_BOLA_DANO, tipo="demonio"))
        if self.particulas: self.particulas.emitir(bx, by, [(180, 30, 255), (255, 100, 255)], 15, vel=5, vida=25, tam=7)
        return True

    # --- ACTUALIZAR CON CLIC_ATACAR ---
    def actualizar(self, teclas, objetivos, puede_atacar=True, clic_atacar=False):
        v = self.velocidad
        moviendose = False

        if teclas[pygame.K_a]:
            self.rect.x -= v
            moviendose = True
            if self.golpe_t == 0: self.mirando_derecha = False
        if teclas[pygame.K_d]:
            self.rect.x += v
            moviendose = True
            if self.golpe_t == 0: self.mirando_derecha = True

        self.rect.x = max(0, min(self.rect.x, self.limite_x - self.rect.width))

        if moviendose and self.en_suelo:
            self.anim_t += 1
            if self.anim_t >= 8:
                self.anim_t = 0
                self.frame = 1 - self.frame
                if self.particulas and self.frame == 1 and not self.dragon_trans: self.particulas.emitir_polvo(self.rect.centerx, self.rect.bottom, 2)
        else:
            self.frame = 0
            self.anim_t = 0

        if self.trans_activa:
            if moviendose and self.en_suelo:
                self.huella_timer += 1
                if self.huella_timer >= 10:
                    self.huella_timer = 0
                    self.huella_paso = 1 - self.huella_paso
                    self.huellas.append({"x": self.rect.centerx + (-6 if self.huella_paso == 0 else 6), "y": self.rect.bottom - 2, "timer": 180, "mirando_derecha": self.mirando_derecha})
            else: self.huella_timer = 0
        else: self.huella_timer = 0

        for h in self.huellas[:]:
            h["timer"] -= 1
            if h["timer"] <= 0: self.huellas.remove(h)

        if self.armadura_equipada and self.particulas:
            self.aura_t += 1
            if self.aura_t > 3:
                self.particulas.emitir_aura_fuego(self.rect.centerx, self.rect.centery)
                self.aura_t = 0

        if self.trans_activa and self.particulas:
            if self.aura_t % 2 == 0: self.particulas.emitir(self.rect.centerx + random.randint(-25, 25), self.rect.centery + random.randint(-30, 20), [(255, 140, 40), (255, 200, 80)], 2, vel=2.0, vida=30, tam=6, gravedad=-0.15)
            self.pulso_aura = (self.pulso_aura + 0.08) % (2 * math.pi)

        if self.dragon_trans and self.particulas:
            self.dragon_aura_pulso = (self.dragon_aura_pulso + 0.1) % (2 * math.pi)
            if self.aura_t % 2 == 0: self.particulas.emitir(self.rect.centerx + random.randint(-30, 30), self.rect.centery + random.randint(-40, 30), [(255, 100, 30), (200, 40, 30)], 2, vel=2.2, vida=35, tam=7, gravedad=-0.2)

        if self.demonio_trans and self.particulas:
            self.demonio_aura_pulso = (self.demonio_aura_pulso + 0.1) % (2 * math.pi)
            if self.aura_t % 2 == 0: self.particulas.emitir(self.rect.centerx + random.randint(-30, 30), self.rect.centery + random.randint(-40, 30), [(150, 30, 200), (60, 0, 90), (255, 50, 150)], 2, vel=2.2, vida=35, tam=7, gravedad=-0.2)

        # --- ALIENTO DE FUEGO DEL DRAGÓN (Usa clic_atacar) ---
        if self.dragon_trans:
            if clic_atacar and self.dragon_aliento_cd <= 0:
                self.dragon_aliento_cd = 6
                bx = self.rect.right + 10 if self.mirando_derecha else self.rect.left - 10
                by = self.rect.centery - 5
                vx = 15 if self.mirando_derecha else -15
                
                for _ in range(3):
                    self.bolas_fuego.append(ProyectilFuego(
                        bx, by + random.randint(-10, 10), 
                        vx + random.uniform(-3, 3), 
                        random.uniform(-2, 2), 
                        DRAGON_BOLA_DANO, tipo="dragon"
                    ))
                if self.particulas:
                    self.particulas.emitir(bx, by, [(255, 220, 90), (255, 120, 30)], 5, vel=5, vida=15, tam=8)

            if teclas[pygame.K_SPACE]:
                self.volando = True
                self.vy += DRAGON_VUELO_SUBIR
                if self.vy < DRAGON_VUELO_MAX_UP: self.vy = DRAGON_VUELO_MAX_UP
            else:
                self.volando = False
                self.vy += DRAGON_VUELO_GRAVEDAD
                if self.vy > 10: self.vy = 10

            if self.rect.y < 20:
                self.rect.y = 20
                self.vy = max(0, self.vy)

            self.rect.y += int(self.vy)
            if self.rect.bottom >= SUELO:
                self.rect.bottom = SUELO
                self.vy = 0
                self.en_suelo = True
            else: self.en_suelo = False
            self.dragon_ala_t += 1
        else:
            self.vy += GRAVEDAD
            self.rect.y += int(self.vy)
            if self.rect.bottom >= SUELO:
                if not self.en_suelo and self.vy > 10:
                    if self.particulas: self.particulas.emitir_polvo(self.rect.centerx, self.rect.bottom, 10)
                self.rect.bottom = SUELO
                self.vy = 0
                self.en_suelo = True

        if self.invulnerable > 0: self.invulnerable -= 1
        if self.ataque_cd > 0: self.ataque_cd -= 1
        if self.z_cd > 0: self.z_cd -= 1
        if self.z_anim_t > 0: self.z_anim_t -= 1
        if self.trans_cd > 0: self.trans_cd -= 1
        if self.trans_anim_t > 0: self.trans_anim_t -= 1
        if self.dragon_trans_cd > 0: self.dragon_trans_cd -= 1
        if self.dragon_anim_t > 0: self.dragon_anim_t -= 1
        if self.dragon_aliento_cd > 0: self.dragon_aliento_cd -= 1
        if self.demonio_trans_cd > 0: self.demonio_trans_cd -= 1
        if self.demonio_anim_t > 0: self.demonio_anim_t -= 1
        if self.demonio_bola_cd > 0: self.demonio_bola_cd -= 1

        # --- ATAQUE CUERPO A CUERPO (Usa clic_atacar) ---
        atacar_cc = (puede_atacar and clic_atacar and self.ataque_cd == 0 and self.golpe_t == 0 and not self.dragon_trans)
        if atacar_cc:
            self.ataque_cd = self.cooldown
            self.golpe_t = DURACION_GOLPE
            self.golpe_aplicado = False
            self.dir_golpe = self.mirando_derecha

        if self.golpe_t > 0:
            self.golpe_t -= 1
            if not self.golpe_aplicado and self.golpe_t <= DURACION_GOLPE // 2:
                self.golpe_aplicado = True
                if self.dir_golpe: hitbox = pygame.Rect(self.rect.right, self.rect.y, 90, self.rect.height)
                else: hitbox = pygame.Rect(self.rect.x - 90, self.rect.y, 90, self.rect.height)
                
                for obj in objetivos:
                    if hitbox.colliderect(obj.rect):
                        obj.recibir_golpe(self.dano, 25 if self.dir_golpe else -25)
                        if self._es_demonio():
                            heal = int(self.dano * 0.15)
                            self.vida = min(self.vida_max, self.vida + heal)
                            if self.particulas: self.particulas.emitir(obj.rect.centerx, obj.rect.centery, [(255, 50, 50), (150, 30, 200)], 8, vel=3, vida=20, tam=5)

                        if self.espada_equipada and self.particulas:
                            self.particulas.emitir(obj.rect.centerx, obj.rect.centery, [(255, 100, 0), (255, 200, 0)], 12, vel=4, vida=20, tam=6)

        for b in self.bolas_fuego[:]:
            b.actualizar(objetivos, self.particulas)
            if not b.viva: self.bolas_fuego.remove(b)
            
        for b in self.bolas_infernales[:]:
            b.actualizar(objetivos, self.particulas)
            if not b.viva: self.bolas_infernales.remove(b)

        self.vida = min(self.vida, self.vida_max)

    # ================== DIBUJOS ==================
    def _dibujar_aura_demonio(self, pantalla, cam_x, t):
        cx = self.rect.centerx - cam_x
        cy = self.rect.centery
        pulso = 1.0 + 0.2 * math.sin(self.demonio_aura_pulso)
        radio_base = 50 * pulso
        for mult, color, alpha_max in [(1.8, (60, 0, 90), 40), (1.4, (150, 30, 200), 60), (1.0, (255, 50, 150), 80)]:
            radio = int(radio_base * mult)
            surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            alpha = int(alpha_max * (0.7 + 0.3 * math.sin(self.demonio_aura_pulso * 2)))
            pygame.draw.circle(surf, (*color, alpha), (radio, radio), radio)
            pantalla.blit(surf, (cx - radio, cy - radio))
        for i in range(8):
            ang = (t / 400 + i * math.tau / 8) % math.tau
            dist = radio_base * 1.3
            px, py = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist
            r = int(6 + 3 * math.sin(t / 100 + i))
            pygame.draw.circle(pantalla, (150, 30, 200), (int(px), int(py)), r)
            pygame.draw.circle(pantalla, (255, 150, 255), (int(px), int(py)), max(1, r // 2))

    def _dibujar_demonio(self, pantalla, cam_x, t):
        r = self.rect
        cx = r.centerx - cam_x
        cy = r.centery
        resp = math.sin(t / 200) * 1.5
        piel_roja = (200, 40, 50)
        rojo_osc = (130, 20, 30)
        cuerno_col = (240, 220, 200)
        ala_col = (80, 20, 80)
        ojo_col = (255, 255, 0)
        negro = (20, 0, 0)

        aleteo = math.sin(t / 150) * 8
        ala_izq = [(cx - 10, cy - 5 + resp), (cx - 45, cy - 35 - aleteo), (cx - 60, cy - 10), (cx - 40, cy + 10)]
        ala_der = [(cx + 10, cy - 5 + resp), (cx + 45, cy - 35 - aleteo), (cx + 60, cy - 10), (cx + 40, cy + 10)]
        pygame.draw.polygon(pantalla, ala_col, ala_izq); pygame.draw.polygon(pantalla, negro, ala_izq, 2)
        pygame.draw.polygon(pantalla, ala_col, ala_der); pygame.draw.polygon(pantalla, negro, ala_der, 2)
        
        pygame.draw.line(pantalla, (150, 30, 200), (cx - 10, cy - 5 + resp), (cx - 45, cy - 35 - aleteo), 2)
        pygame.draw.line(pantalla, (150, 30, 200), (cx + 10, cy - 5 + resp), (cx + 45, cy - 35 - aleteo), 2)

        cola_puntos = []
        for k in range(5):
            frac = k / 4
            tx = cx - 15 - frac * 35 if self.mirando_derecha else cx + 15 + frac * 35
            ty = cy + 15 + frac * 15 + math.sin(t / 120 + k) * 4
            cola_puntos.append((tx, ty))
        for k in range(len(cola_puntos) - 1):
            pygame.draw.line(pantalla, piel_roja, cola_puntos[k], cola_puntos[k + 1], 8 - k)
        punta = cola_puntos[-1]
        dir_x = -1 if self.mirando_derecha else 1
        pygame.draw.polygon(pantalla, (150, 30, 200), [(punta[0], punta[1] - 6), (punta[0] + dir_x * 15, punta[1]), (punta[0], punta[1] + 6)])

        cuerpo_rect = pygame.Rect(cx - 18, cy - 10 + resp, 36, 45)
        pygame.draw.ellipse(pantalla, piel_roja, cuerpo_rect)
        pygame.draw.ellipse(pantalla, rojo_osc, cuerpo_rect, 2)
        
        pata_y = r.bottom - 8
        pygame.draw.ellipse(pantalla, rojo_osc, (cx - 14, pata_y - 5, 10, 8))
        pygame.draw.ellipse(pantalla, rojo_osc, (cx + 4, pata_y - 5, 10, 8))
        pygame.draw.circle(pantalla, (200, 200, 200), (cx - 12, pata_y + 2), 2)
        pygame.draw.circle(pantalla, (200, 200, 200), (cx + 6, pata_y + 2), 2)

        cabeza_y = cy - 25 + resp
        cabeza_rect = pygame.Rect(cx - 16, cabeza_y - 12, 32, 30)
        pygame.draw.ellipse(pantalla, piel_roja, cabeza_rect)
        pygame.draw.ellipse(pantalla, rojo_osc, cabeza_rect, 2)

        cuerno_izq = [(cx - 12, cabeza_y - 10), (cx - 20, cabeza_y - 35), (cx - 6, cabeza_y - 14)]
        cuerno_der = [(cx + 12, cabeza_y - 10), (cx + 20, cabeza_y - 35), (cx + 6, cabeza_y - 14)]
        pygame.draw.polygon(pantalla, cuerno_col, cuerno_izq)
        pygame.draw.polygon(pantalla, (150, 150, 150), cuerno_izq, 2)
        pygame.draw.polygon(pantalla, cuerno_col, cuerno_der)
        pygame.draw.polygon(pantalla, (150, 150, 150), cuerno_der, 2)

        ojo_y = cabeza_y + 2
        if self.mirando_derecha:
            pygame.draw.circle(pantalla, ojo_col, (cx + 6, ojo_y), 4)
            pygame.draw.circle(pantalla, negro, (cx + 7, ojo_y), 2)
            pygame.draw.circle(pantalla, ojo_col, (cx - 4, ojo_y), 4)
            pygame.draw.circle(pantalla, negro, (cx - 5, ojo_y), 2)
        else:
            pygame.draw.circle(pantalla, ojo_col, (cx - 6, ojo_y), 4)
            pygame.draw.circle(pantalla, negro, (cx - 7, ojo_y), 2)
            pygame.draw.circle(pantalla, ojo_col, (cx + 4, ojo_y), 4)
            pygame.draw.circle(pantalla, negro, (cx + 5, ojo_y), 2)

        pygame.draw.arc(pantalla, negro, (cx - 8, cabeza_y + 6, 16, 10), 0.2, 2.9, 2)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx - 5, cabeza_y + 12), 1)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx + 5, cabeza_y + 12), 1)

    def _dibujar_huellas(self, pantalla, cam_x):
        for h in self.huellas:
            sx, sy = int(h["x"] - cam_x), int(h["y"])
            alpha = min(255, int(h["timer"] * 255 / 60))
            if alpha <= 0: continue
            surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            color = (255, 140, 40, alpha)
            color_oscuro = (200, 90, 20, alpha)
            pygame.draw.ellipse(surf, color_oscuro, (5, 10, 10, 7))
            pygame.draw.ellipse(surf, color, (6, 3, 8, 8))
            pygame.draw.circle(surf, color, (3, 4), 2)
            pygame.draw.circle(surf, color, (10, 2), 2)
            pygame.draw.circle(surf, color, (17, 4), 2)
            pantalla.blit(surf, (sx - 10, sy - 15))

    def _dibujar_colas_kitsune(self, pantalla, cam_x, t):
        r = self.rect
        base_x = r.x - cam_x + (10 if self.mirando_derecha else r.width - 10)
        base_y = r.centery + 10
        trans = self.trans_activa
        escala = 1.5 if trans else 1.0
        colores = [(255, 100, 20), (255, 140, 40), (255, 180, 60), (255, 210, 100), (255, 240, 150), (255, 255, 220)] if trans else [(200, 110, 40), (230, 130, 45), (245, 160, 60), (255, 190, 90), (255, 215, 130), (255, 240, 200)]
        
        for i in range(9):
            offset = 0 if self.mirando_derecha else 180
            ang = math.radians(160 + i * 12 + offset + math.sin(t / 250 + i * 0.7) * 8)
            largo = (60 + i * 3) * escala
            grosor = max(4, int((12 - i * 0.6) * escala))
            pts = []
            for k in range(8):
                frac = k / 7
                dist = largo * frac
                px = base_x + math.cos(ang) * dist + math.sin(t / 200 + i * 0.5 + k * 0.8) * (3 + k * 1.5) * escala
                py = base_y + math.sin(ang) * dist + math.cos(t / 300 + i * 0.4 + k * 0.6) * (2 + k * 1.2) * escala
                pts.append((px, py))
            for k in range(len(pts) - 1):
                c = colores[min(k, len(colores) - 1)]
                pygame.draw.line(pantalla, c, pts[k], pts[k + 1], max(2, grosor - k))
                if k < len(pts) - 2:
                    pygame.draw.circle(pantalla, tuple(min(255, v + 40) for v in c), (int(pts[k][0]), int(pts[k][1])), max(1, (grosor - k) // 2))
            punta = pts[-1]
            pygame.draw.circle(pantalla, (255, 255, 220), (int(punta[0]), int(punta[1])), max(2, int(5 * escala)))
            pygame.draw.circle(pantalla, (255, 255, 255), (int(punta[0]), int(punta[1])), max(1, int(2 * escala)))
            if trans:
                halo = pygame.Surface((int(30 * escala), int(30 * escala)), pygame.SRCALPHA)
                alpha_pulse = int(120 + 80 * math.sin(t / 100 + i))
                pygame.draw.circle(halo, (255, 200, 80, alpha_pulse), (halo.get_width() // 2, halo.get_height() // 2), int(12 * escala))
                pygame.draw.circle(halo, (255, 255, 200, alpha_pulse // 2), (halo.get_width() // 2, halo.get_height() // 2), int(6 * escala))
                pantalla.blit(halo, (punta[0] - halo.get_width() // 2, punta[1] - halo.get_height() // 2))

    def _dibujar_aura_transformacion(self, pantalla, cam_x, t):
        cx, cy = self.rect.centerx - cam_x, self.rect.centery
        pulso = 1.0 + 0.15 * math.sin(self.pulso_aura)
        radio_base = 45 * pulso
        for mult, color, alpha_max in [(1.8, (255, 100, 20), 40), (1.4, (255, 160, 40), 60), (1.1, (255, 220, 100), 80), (0.8, (255, 255, 200), 100)]:
            radio = int(radio_base * mult)
            surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, int(alpha_max * (0.7 + 0.3 * math.sin(self.pulso_aura * 2)))), (radio, radio), radio)
            pantalla.blit(surf, (cx - radio, cy - radio))
        for i in range(8):
            ang = (t / 400 + i * math.tau / 8) % math.tau
            px, py = cx + math.cos(ang) * (radio_base * 1.3), cy + math.sin(ang) * (radio_base * 1.3)
            r = int(6 + 3 * math.sin(t / 100 + i))
            pygame.draw.circle(pantalla, (255, 200, 80), (int(px), int(py)), r)
            pygame.draw.circle(pantalla, (255, 255, 200), (int(px), int(py)), max(1, r // 2))

    def _dibujar_aura_dragon(self, pantalla, cam_x, t):
        cx, cy = self.rect.centerx - cam_x, self.rect.centery
        pulso = 1.0 + 0.2 * math.sin(self.dragon_aura_pulso)
        radio_base = 55 * pulso
        for mult, color, alpha_max in [(2.0, (200, 30, 20), 35), (1.6, (255, 80, 20), 55), (1.2, (255, 160, 40), 75), (0.85, (255, 220, 100), 95)]:
            radio = int(radio_base * mult)
            surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, int(alpha_max * (0.7 + 0.3 * math.sin(self.dragon_aura_pulso * 2)))), (radio, radio), radio)
            pantalla.blit(surf, (cx - radio, cy - radio))
        for i in range(10):
            ang = (t / 350 + i * math.tau / 10) % math.tau
            px, py = cx + math.cos(ang) * (radio_base * 1.4), cy + math.sin(ang) * (radio_base * 1.4)
            r = int(5 + 3 * math.sin(t / 80 + i))
            pygame.draw.circle(pantalla, (255, 100, 30), (int(px), int(py)), r + 2)
            pygame.draw.circle(pantalla, (255, 200, 80), (int(px), int(py)), r)

    def _dibujar_onda_transformacion(self, pantalla, cam_x):
        if self.trans_anim_t <= 0: return
        cx, cy = self.rect.centerx - cam_x, self.rect.centery
        radio = int(30 + 180 * (1 - self.trans_anim_t / 25))
        alpha = int(255 * (self.trans_anim_t / 25))
        color1 = (255, 180, 40) if self.trans_anim_tipo == "on" else (255, 220, 120)
        color2 = (255, 240, 150) if self.trans_anim_tipo == "on" else (255, 255, 220)
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color1, alpha), (radio, radio), radio, 6)
        pygame.draw.circle(surf, (*color2, alpha), (radio, radio), max(1, radio - 25), 3)
        pantalla.blit(surf, (cx - radio, cy - radio))

    def _dibujar_onda_dragon(self, pantalla, cam_x):
        if self.dragon_anim_t <= 0: return
        cx, cy = self.rect.centerx - cam_x, self.rect.centery
        radio = int(40 + 220 * (1 - self.dragon_anim_t / 28))
        alpha = int(255 * (self.dragon_anim_t / 28))
        color1 = (200, 40, 30) if self.dragon_anim_tipo == "on" else (255, 140, 60)
        color2 = (255, 200, 60) if self.dragon_anim_tipo == "on" else (255, 220, 120)
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color1, alpha), (radio, radio), radio, 8)
        pygame.draw.circle(surf, (*color2, alpha), (radio, radio), max(1, radio - 30), 4)
        pantalla.blit(surf, (cx - radio, cy - radio))

    def _dibujar_onda_demonio(self, pantalla, cam_x):
        if self.demonio_anim_t <= 0: return
        cx, cy = self.rect.centerx - cam_x, self.rect.centery
        radio = int(40 + 220 * (1 - self.demonio_anim_t / 28))
        alpha = int(255 * (self.demonio_anim_t / 28))
        color1 = (150, 30, 200) if self.demonio_anim_tipo == "on" else (255, 50, 150)
        color2 = (255, 100, 255) if self.demonio_anim_tipo == "on" else (255, 200, 255)
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color1, alpha), (radio, radio), radio, 8)
        pygame.draw.circle(surf, (*color2, alpha), (radio, radio), max(1, radio - 30), 4)
        pantalla.blit(surf, (cx - radio, cy - radio))

    def _dibujar_kitsune(self, pantalla, cam_x, t):
        r = self.rect
        cx, cy = r.centerx - cam_x, r.centery
        resp = math.sin(t / 250) * 1.5
        naranja, naranja_osc, naranja_brillo, crema, blanco, negro = (255, 140, 40), (220, 100, 20), (255, 180, 80), (255, 240, 200), (255, 255, 255), (40, 20, 10)
        pygame.draw.ellipse(pantalla, naranja, pygame.Rect(cx - 22, cy - 8 + resp, 44, 45))
        pygame.draw.ellipse(pantalla, naranja_osc, pygame.Rect(cx - 22, cy - 8 + resp, 44, 45), 2)
        pygame.draw.ellipse(pantalla, crema, pygame.Rect(cx - 12, cy + 2 + resp, 24, 30))
        pata_y = r.bottom - 8
        pygame.draw.ellipse(pantalla, naranja_osc, (cx - 14, pata_y - 4, 10, 8))
        pygame.draw.ellipse(pantalla, naranja_osc, (cx + 4, pata_y - 4, 10, 8))
        pygame.draw.ellipse(pantalla, blanco, (cx - 12, pata_y, 6, 4))
        pygame.draw.ellipse(pantalla, blanco, (cx + 6, pata_y, 6, 4))
        cabeza_y = cy - 22 + resp
        pygame.draw.ellipse(pantalla, naranja, pygame.Rect(cx - 16, cabeza_y - 12, 32, 28))
        pygame.draw.ellipse(pantalla, naranja_osc, pygame.Rect(cx - 16, cabeza_y - 12, 32, 28), 2)
        oreja_izq = [(cx - 14, cabeza_y - 6), (cx - 18, cabeza_y - 26), (cx - 6, cabeza_y - 10)]
        oreja_der = [(cx + 14, cabeza_y - 6), (cx + 18, cabeza_y - 26), (cx + 6, cabeza_y - 10)]
        pygame.draw.polygon(pantalla, naranja, oreja_izq); pygame.draw.polygon(pantalla, naranja_osc, oreja_izq, 2)
        pygame.draw.polygon(pantalla, naranja, oreja_der); pygame.draw.polygon(pantalla, naranja_osc, oreja_der, 2)
        pygame.draw.polygon(pantalla, (255, 200, 180), [(cx - 12, cabeza_y - 8), (cx - 16, cabeza_y - 22), (cx - 7, cabeza_y - 11)])
        pygame.draw.polygon(pantalla, (255, 200, 180), [(cx + 12, cabeza_y - 8), (cx + 16, cabeza_y - 22), (cx + 7, cabeza_y - 11)])
        pygame.draw.ellipse(pantalla, crema, pygame.Rect(cx - 10, cabeza_y + 4, 20, 12))
        ojo_y = cabeza_y + 2
        pygame.draw.ellipse(pantalla, blanco, (cx - 10, ojo_y, 7, 5)); pygame.draw.ellipse(pantalla, negro, (cx - 7, ojo_y + 1, 3, 3))
        pygame.draw.ellipse(pantalla, blanco, (cx + 3, ojo_y, 7, 5)); pygame.draw.ellipse(pantalla, negro, (cx + 5, ojo_y + 1, 3, 3))
        pygame.draw.polygon(pantalla, negro, [(cx - 2, cabeza_y + 10), (cx + 2, cabeza_y + 10), (cx, cabeza_y + 12)])
        pygame.draw.arc(pantalla, negro, (cx - 4, cabeza_y + 11, 8, 5), 0.3, 2.8, 1)
        pygame.draw.line(pantalla, negro, (cx - 10, cabeza_y + 11), (cx - 16, cabeza_y + 9), 1); pygame.draw.line(pantalla, negro, (cx - 10, cabeza_y + 13), (cx - 16, cabeza_y + 14), 1)
        pygame.draw.line(pantalla, negro, (cx + 10, cabeza_y + 11), (cx + 16, cabeza_y + 9), 1); pygame.draw.line(pantalla, negro, (cx + 10, cabeza_y + 13), (cx + 16, cabeza_y + 14), 1)
        pygame.draw.arc(pantalla, naranja_brillo, pygame.Rect(cx - 16, cabeza_y - 12, 32, 28), 0.5, 2.5, 2)
        pygame.draw.polygon(pantalla, (220, 40, 40), [(cx, cabeza_y - 4), (cx - 3, cabeza_y - 1), (cx, cabeza_y + 2), (cx + 3, cabeza_y - 1)])

    def _dibujar_dragon(self, pantalla, cam_x, t):
        r = self.rect
        cx, cy = r.centerx - cam_x, r.centery
        resp = math.sin(t / 200) * 2
        rojo, rojo_osc, rojo_brillo, naranja, amarillo, crema, negro, blanco = (200, 40, 30), (140, 20, 20), (255, 80, 40), (255, 120, 30), (255, 220, 60), (255, 230, 180), (30, 10, 10), (255, 255, 255)
        aleteo = math.sin(t / 80) * 18 if self.volando else (math.sin(t / 120) * 12 if not self.en_suelo else math.sin(t / 300) * 4)
        ala_izq = [(cx - 5, cy - 10 + resp), (cx - 55, cy - 50 - aleteo + resp), (cx - 75, cy - 20 - aleteo + resp), (cx - 65, cy + 5 + resp), (cx - 40, cy + 10 + resp), (cx - 10, cy + 5 + resp)]
        pygame.draw.polygon(pantalla, rojo_osc, ala_izq); pygame.draw.polygon(pantalla, negro, ala_izq, 2)
        pygame.draw.line(pantalla, rojo, (cx - 5, cy - 10 + resp), (cx - 55, cy - 50 - aleteo + resp), 2)
        pygame.draw.line(pantalla, rojo, (cx - 5, cy - 10 + resp), (cx - 75, cy - 20 - aleteo + resp), 2)
        pygame.draw.line(pantalla, rojo, (cx - 5, cy - 10 + resp), (cx - 65, cy + 5 + resp), 2)
        ala_der = [(cx + 5, cy - 10 + resp), (cx + 55, cy - 50 - aleteo + resp), (cx + 75, cy - 20 - aleteo + resp), (cx + 65, cy + 5 + resp), (cx + 40, cy + 10 + resp), (cx + 10, cy + 5 + resp)]
        pygame.draw.polygon(pantalla, rojo_osc, ala_der); pygame.draw.polygon(pantalla, negro, ala_der, 2)
        pygame.draw.line(pantalla, rojo, (cx + 5, cy - 10 + resp), (cx + 55, cy - 50 - aleteo + resp), 2)
        pygame.draw.line(pantalla, rojo, (cx + 5, cy - 10 + resp), (cx + 75, cy - 20 - aleteo + resp), 2)
        pygame.draw.line(pantalla, rojo, (cx + 5, cy - 10 + resp), (cx + 65, cy + 5 + resp), 2)
        cola_puntos = [(cx - 20 - (k/5)*45 if self.mirando_derecha else cx + 20 + (k/5)*45, cy + 15 + (k/5)*20 + math.sin(t / 150 + k) * 5) for k in range(6)]
        for k in range(len(cola_puntos) - 1):
            pygame.draw.line(pantalla, rojo, cola_puntos[k], cola_puntos[k + 1], max(3, 12 - k * 2))
            pygame.draw.line(pantalla, rojo_osc, cola_puntos[k], cola_puntos[k + 1], max(1, 8 - k * 2))
        punta = cola_puntos[-1]
        dir_x = -1 if self.mirando_derecha else 1
        pygame.draw.polygon(pantalla, naranja, [(punta[0], punta[1] - 10), (punta[0] + dir_x * 20, punta[1]), (punta[0], punta[1] + 10)])
        pygame.draw.polygon(pantalla, rojo_osc, [(punta[0], punta[1] - 10), (punta[0] + dir_x * 20, punta[1]), (punta[0], punta[1] + 10)], 2)
        pygame.draw.ellipse(pantalla, rojo, pygame.Rect(cx - 28, cy - 12 + resp, 56, 50))
        pygame.draw.ellipse(pantalla, rojo_osc, pygame.Rect(cx - 28, cy - 12 + resp, 56, 50), 2)
        pygame.draw.ellipse(pantalla, crema, pygame.Rect(cx - 16, cy - 2 + resp, 32, 38))
        for ly in range(int(cy + resp), int(cy + 30 + resp), 6): pygame.draw.arc(pantalla, (220, 180, 130), (cx - 15, ly, 30, 8), 3.4, 6.0, 1)
        pata_y = r.bottom - 10
        pygame.draw.ellipse(pantalla, rojo_osc, (cx - 20, pata_y - 6, 14, 10)); pygame.draw.ellipse(pantalla, rojo_osc, (cx + 6, pata_y - 6, 14, 10))
        pygame.draw.circle(pantalla, blanco, (cx - 16, pata_y + 2), 2); pygame.draw.circle(pantalla, blanco, (cx - 10, pata_y + 2), 2)
        pygame.draw.circle(pantalla, blanco, (cx + 10, pata_y + 2), 2); pygame.draw.circle(pantalla, blanco, (cx + 16, pata_y + 2), 2)
        cabeza_y = cy - 28 + resp
        pygame.draw.ellipse(pantalla, rojo, pygame.Rect(cx - 22, cabeza_y - 16, 44, 36))
        pygame.draw.ellipse(pantalla, rojo_osc, pygame.Rect(cx - 22, cabeza_y - 16, 44, 36), 2)
        cuerno_izq = [(cx - 18, cabeza_y - 12), (cx - 28, cabeza_y - 40), (cx - 22, cabeza_y - 44), (cx - 10, cabeza_y - 16)]
        cuerno_der = [(cx + 18, cabeza_y - 12), (cx + 28, cabeza_y - 40), (cx + 22, cabeza_y - 44), (cx + 10, cabeza_y - 16)]
        pygame.draw.polygon(pantalla, crema, cuerno_izq); pygame.draw.polygon(pantalla, (180, 140, 80), cuerno_izq, 2)
        pygame.draw.polygon(pantalla, crema, cuerno_der); pygame.draw.polygon(pantalla, (180, 140, 80), cuerno_der, 2)
        pygame.draw.circle(pantalla, (200, 160, 100), (cx - 22, cabeza_y - 42), 3); pygame.draw.circle(pantalla, (200, 160, 100), (cx + 22, cabeza_y - 42), 3)
        for i in range(3):
            sx, sy = cx - 10 + i * 10, cabeza_y - 12
            pygame.draw.polygon(pantalla, naranja, [(sx - 4, sy), (sx, sy - 12), (sx + 4, sy)])
            pygame.draw.polygon(pantalla, rojo_osc, [(sx - 4, sy), (sx, sy - 12), (sx + 4, sy)], 1)
        hocico_x = cx + 15 if self.mirando_derecha else cx - 15
        pygame.draw.ellipse(pantalla, crema, pygame.Rect(hocico_x - 10, cabeza_y + 4, 20, 14))
        pygame.draw.ellipse(pantalla, rojo_osc, pygame.Rect(hocico_x - 10, cabeza_y + 4, 20, 14), 1)
        ojo_y = cabeza_y + 2
        ojo_x = cx + 6 if self.mirando_derecha else cx - 12
        pygame.draw.ellipse(pantalla, amarillo, (ojo_x, ojo_y, 8, 6)); pygame.draw.ellipse(pantalla, negro, (ojo_x + 3, ojo_y + 1, 2, 4)); pygame.draw.circle(pantalla, blanco, (ojo_x + 4, ojo_y + 2), 1)
        ojo2_x = cx + 1 if self.mirando_derecha else cx - 8
        pygame.draw.ellipse(pantalla, amarillo, (ojo2_x, ojo_y - 2, 6, 4)); pygame.draw.ellipse(pantalla, negro, (ojo2_x + 2, ojo_y - 1, 2, 2))
        nariz_x = cx + 22 if self.mirando_derecha else cx - 22
        pygame.draw.circle(pantalla, negro, (nariz_x, cabeza_y + 10), 1); pygame.draw.circle(pantalla, negro, (nariz_x + (2 if self.mirando_derecha else -2), cabeza_y + 10), 1)
        if self.dragon_aliento_cd > 0:
            boca_rect = pygame.Rect(cx + 20, cabeza_y + 12, 12, 8) if self.mirando_derecha else pygame.Rect(cx - 32, cabeza_y + 12, 12, 8)
            pygame.draw.ellipse(pantalla, (60, 10, 10), boca_rect); pygame.draw.ellipse(pantalla, naranja, boca_rect, 2)
            pygame.draw.circle(pantalla, amarillo, boca_rect.center, 3); pygame.draw.circle(pantalla, blanco, boca_rect.center, 1)
        pygame.draw.polygon(pantalla, naranja, [(cx, cabeza_y - 6), (cx - 5, cabeza_y - 2), (cx - 3, cabeza_y + 2), (cx + 3, cabeza_y + 2), (cx + 5, cabeza_y - 2)])
        pygame.draw.polygon(pantalla, amarillo, [(cx, cabeza_y - 4), (cx - 3, cabeza_y - 1), (cx - 2, cabeza_y + 1), (cx + 2, cabeza_y + 1), (cx + 3, cabeza_y - 1)])

    def _dibujar_espada(self, pantalla, mano, angulo, cam_x):
        img_original = SPRITE_ESPADA
        if self.espada_equipada:
            img_original = SPRITE_ESPADA.copy()
            img_original.fill((255, 120, 30), special_flags=pygame.BLEND_RGBA_MULT)
        w, h = img_original.get_size()
        pivote = pygame.math.Vector2(w / 2, 50)
        centro = pygame.math.Vector2(w / 2, h / 2)
        desfase = (pivote - centro).rotate(-angulo)
        img = pygame.transform.rotate(img_original, angulo)
        r = img.get_rect(center=(mano[0] - desfase.x, mano[1] - desfase.y))
        pantalla.blit(img, r)
        if self.espada_equipada and self.golpe_t > 0 and self.particulas:
            self.particulas.emitir_estela_fuego(mano[0] + cam_x, mano[1])

    def dibujar(self, pantalla, cam_x):
        r = self.rect
        x = r.x - cam_x
        parpadeo = self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0
        t = pygame.time.get_ticks()

        if self.trans_activa: self._dibujar_huellas(pantalla, cam_x)
        if self.trans_activa: self._dibujar_aura_transformacion(pantalla, cam_x, t)
        if self.dragon_trans: self._dibujar_aura_dragon(pantalla, cam_x, t)
        if self.demonio_trans: self._dibujar_aura_demonio(pantalla, cam_x, t)

        if self._es_kitsune(): self._dibujar_colas_kitsune(pantalla, cam_x, t)

        if not parpadeo:
            if self.dragon_trans: self._dibujar_dragon(pantalla, cam_x, t)
            elif self.demonio_trans: self._dibujar_demonio(pantalla, cam_x, t)
            elif self.trans_activa:
                self._dibujar_kitsune(pantalla, cam_x, t)
                derecha = self.dir_golpe if self.golpe_t > 0 else self.mirando_derecha
                mano = ((x + 48, r.y + 35) if derecha else (x + 2, r.y + 35))
                prog = 0
                if self.golpe_t > 0: prog = 1 - self.golpe_t / DURACION_GOLPE; ang = 90 - 190 * prog
                else: ang = -35
                if not derecha: ang = -ang
                self._dibujar_espada(pantalla, mano, ang, cam_x)
                if self.golpe_t > 0 and prog >= 0.3:
                    caja = pygame.Rect(0, 0, 150, 150); caja.center = mano
                    if derecha: ang1, ang2 = -1.1, 1.0
                    else: ang1, ang2 = 3.14159 - 1.0, 3.14159 + 1.1
                    if self.espada_equipada:
                        pygame.draw.arc(pantalla, (255, 100, 0), caja, ang1, ang2, 6)
                        pygame.draw.arc(pantalla, (255, 200, 0), caja, ang1, ang2, 2)
                    else: pygame.draw.arc(pantalla, BLANCO, caja, ang1, ang2, 4)
            else:
                sprite = SPRITE_HEROE_1 if self.frame == 0 else SPRITE_HEROE_2
                if not self.mirando_derecha: sprite = SPRITE_HEROE_1_IZQ if self.frame == 0 else SPRITE_HEROE_2_IZQ
                offset_y = 5 if self.golpe_t > 0 else 0
                pantalla.blit(sprite, (x, r.y + offset_y))
                if self.armadura_equipada:
                    armadura_sprite = SPRITE_ARMADURA if self.mirando_derecha else SPRITE_ARMADURA_IZQ
                    pantalla.blit(armadura_sprite, (x, r.y + offset_y))
                derecha = self.dir_golpe if self.golpe_t > 0 else self.mirando_derecha
                mano = ((x + 42, r.y + 43 + offset_y) if derecha else (x + 8, r.y + 43 + offset_y))
                prog = 0
                if self.golpe_t > 0: prog = 1 - self.golpe_t / DURACION_GOLPE; ang = 90 - 190 * prog
                else: ang = -35
                if not derecha: ang = -ang
                self._dibujar_espada(pantalla, mano, ang, cam_x)
                if self.golpe_t > 0 and prog >= 0.3:
                    caja = pygame.Rect(0, 0, 150, 150); caja.center = mano
                    if derecha: ang1, ang2 = -1.1, 1.0
                    else: ang1, ang2 = 3.14159 - 1.0, 3.14159 + 1.1
                    if self.espada_equipada:
                        pygame.draw.arc(pantalla, (255, 100, 0), caja, ang1, ang2, 6)
                        pygame.draw.arc(pantalla, (255, 200, 0), caja, ang1, ang2, 2)
                    else: pygame.draw.arc(pantalla, BLANCO, caja, ang1, ang2, 4)

        for b in self.bolas_fuego: b.dibujar(pantalla, cam_x)
        for b in self.bolas_infernales: b.dibujar(pantalla, cam_x)

        if self.z_anim_t > 0:
            radio_actual = int(Z_RADIO * (1 - self.z_anim_t / 25))
            alpha = int(255 * (self.z_anim_t / 25))
            onda_surf = pygame.Surface((radio_actual * 2, radio_actual * 2), pygame.SRCALPHA)
            pygame.draw.circle(onda_surf, (255, 100, 0, alpha), (radio_actual, radio_actual), radio_actual, 6)
            pygame.draw.circle(onda_surf, (255, 220, 0, alpha), (radio_actual, radio_actual), max(1, radio_actual - 20), 3)
            pantalla.blit(onda_surf, (self.z_x - cam_x - radio_actual, self.z_y - radio_actual))

        if self.trans_anim_t > 0: self._dibujar_onda_transformacion(pantalla, cam_x)
        if self.dragon_anim_t > 0: self._dibujar_onda_dragon(pantalla, cam_x)
        if self.demonio_anim_t > 0: self._dibujar_onda_demonio(pantalla, cam_x)

        pygame.draw.rect(pantalla, ROJO, (x, r.y - 14, 50, 6))
        pygame.draw.rect(pantalla, VERDE, (x, r.y - 14, 50 * max(self.vida, 0) / self.vida_max, 6))