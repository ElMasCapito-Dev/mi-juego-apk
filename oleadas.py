import random
from config import *
from enemigos import Enemigo
from guardado import guardar
from niveles import ganar_xp
import misiones

class Oleadas:
    def __init__(self, particulas=None):
        self.enemigos = []
        self.spawn_t = 0
        self.particulas = particulas

    def reiniciar(self):
        self.enemigos.clear()
        self.spawn_t = 0

    def actualizar(self, jugador, datos, inventario=None):
        px = jugador.rect.centerx
        zona = 1 + px // ZONA_PX

        if px > CASTILLO_X - 100:
            self.enemigos.clear()
            return

        self.spawn_t += 1
        if self.spawn_t > 100 and len(self.enemigos) < 3:
            for lado in random.sample([-1, 1], 2):
                x = px + lado * random.randint(500, 700)
                if 0 <= x <= CASTILLO_X - 150:
                    hp = 20 + 8 * zona
                    self.enemigos.append(Enemigo(x, hp, self.particulas))
                    self.spawn_t = 0
                    break

        for en in self.enemigos[:]:
            if abs(en.x - px) > 1600:
                self.enemigos.remove(en)
                continue
            en.actualizar(jugador, zona)

        for en in self.enemigos[:]:
            if en.hp <= 0:
                self.enemigos.remove(en)
                datos["oro"] += 5 + 2 * zona
                datos["gemas"] += random.randint(1, 3)
                ganar_xp(datos, 10 + 2 * zona)
                misiones.progreso(datos, "bandidos", 1)
                if inventario is not None and random.random() < 0.70:
                    inventario.agregar("cuero", 1)
                guardar(datos) # <--- Ahora esto funciona sin error

    def dibujar(self, pantalla, cam_x):
        for en in self.enemigos:
            en.dibujar(pantalla, cam_x)