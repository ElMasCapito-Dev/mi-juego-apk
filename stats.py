import pygame
from config import *
from guardado import guardar
from ui import texto, fuente, fuente_chica, COLOR_TEXTO

STATS = [("Poder", "poder"), ("Combate", "combate"), ("Vida", "vida")]

class PanelStats:
    def __init__(self):
        self.abierto = False
        self.boton = pygame.Rect(15, 230, 100, 32)
        self.panel = pygame.Rect(130, 60, 400, 270)

    def _boton_mas(self, i):
        return pygame.Rect(self.panel.right - 50, self.panel.y + 100 + i * 45, 34, 34)

    def _puede_subir(self, clave, datos, jugador):
        if datos["puntos"] <= 0: return False
        if clave == "combate" and jugador.cooldown <= DURACION_GOLPE: return False
        return True

    def mouse_encima(self, pos):
        if self.boton.collidepoint(pos): return True
        return self.abierto and self.panel.collidepoint(pos)

    def click(self, pos, datos, jugador):
        if self.boton.collidepoint(pos):
            self.abierto = not self.abierto
            return
        if not self.abierto: return
        for i, (_, clave) in enumerate(STATS):
            if self._boton_mas(i).collidepoint(pos) and self._puede_subir(clave, datos, jugador):
                datos["puntos"] -= 1
                datos[clave] += 1
                if clave == "vida": jugador.vida += VIDA_POR_PUNTO
                guardar(datos)

    def _detalle(self, clave, jugador):
        if clave == "poder": return f"Dano Z: {jugador.dano_z}"
        if clave == "combate":
            extra = " (MAX)" if jugador.cooldown <= DURACION_GOLPE else ""
            return f"Daño {jugador.dano} | {60 / jugador.cooldown:.1f} golpes/s{extra}"
        return f"{jugador.vida_max} de vida"

    def dibujar(self, pantalla, datos, jugador):
        hay = datos["puntos"] > 0
        pygame.draw.rect(pantalla, AMARILLO if hay else (240, 240, 240), self.boton, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_TEXTO, self.boton, 2, border_radius=6)
        texto(pantalla, f"Stats ({datos['puntos']})" if hay else "Stats", fuente_chica, COLOR_TEXTO, self.boton.x + 10, self.boton.y + 8)

        if not self.abierto: return

        p = self.panel
        fondo = pygame.Surface(p.size, pygame.SRCALPHA)
        pygame.draw.rect(fondo, (250, 245, 225, 240), fondo.get_rect(), border_radius=10)
        pantalla.blit(fondo, p.topleft)
        pygame.draw.rect(pantalla, COLOR_TEXTO, p, 3, border_radius=10)

        texto(pantalla, "Estadísticas", fuente, COLOR_TEXTO, p.x + 15, p.y + 12)
        texto(pantalla, f"Puntos disponibles: {datos['puntos']}", fuente_chica, COLOR_TEXTO, p.x + 15, p.y + 55)

        for i, (nombre, clave) in enumerate(STATS):
            y = p.y + 100 + i * 45
            texto(pantalla, nombre, fuente, COLOR_TEXTO, p.x + 15, y + 6)
            texto(pantalla, str(datos[clave]), fuente, COLOR_TEXTO, p.x + 105, y + 6)
            texto(pantalla, self._detalle(clave, jugador), fuente_chica, COLOR_TEXTO, p.x + 140, y + 9)

            boton = self._boton_mas(i)
            activo = self._puede_subir(clave, datos, jugador)
            pygame.draw.rect(pantalla, VERDE if activo else (190, 190, 190), boton, border_radius=6)
            pygame.draw.rect(pantalla, COLOR_TEXTO, boton, 2, border_radius=6)
            texto(pantalla, "+", fuente, COLOR_TEXTO, boton.x + 10, boton.y + 6)

        raza_info = RAZAS[datos.get("raza", "humano")]
        texto(pantalla, f"Raza: {raza_info['nombre']} ({raza_info['desc']})", fuente_chica, raza_info['color'], p.x + 15, p.y + 240)