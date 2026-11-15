import pygame
from items import ITEMS, es_consumible
from inventario import SLOTS_COLS, SLOTS_FILAS, SLOTS_TOTAL

pygame.font.init()
fuente_titulo = pygame.font.SysFont(None, 32)
fuente_slot = pygame.font.SysFont(None, 20)
fuente_info = pygame.font.SysFont(None, 22)
fuente_chica = pygame.font.SysFont(None, 18)

COLOR_TEXTO = (30, 30, 40)
COLOR_PANEL = (245, 240, 220)
COLOR_BORDE = (60, 40, 20)
COLOR_SLOT = (210, 200, 175)
COLOR_SLOT_BORDE = (120, 100, 70)
COLOR_SLOT_HOVER = (230, 220, 195)
COLOR_SLOT_SEL = (240, 220, 150)

SLOT_SIZE = 64
SLOT_PAD = 6

class UIInventario:
    def __init__(self):
        self.abierto = False
        self.boton = pygame.Rect(120, 230, 100, 32)

        ancho_slots = SLOTS_COLS * SLOT_SIZE + (SLOTS_COLS - 1) * SLOT_PAD
        alto_slots = SLOTS_FILAS * SLOT_SIZE + (SLOTS_FILAS - 1) * SLOT_PAD
        self.panel_w = ancho_slots + 320
        self.panel_h = alto_slots + 100
        self.panel_x = (800 - self.panel_w) // 2
        self.panel_y = (500 - self.panel_h) // 2
        self.panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_w, self.panel_h)
        self.slots_x = self.panel_x + 25
        self.slots_y = self.panel_y + 60

        self.arrastrando = False
        self.arrastre_desde = -1
        self.mouse_offset = (0, 0)
        self.slot_hover = -1
        self.slot_seleccionado = -1

    def _slot_rect(self, idx):
        col = idx % SLOTS_COLS
        fila = idx // SLOTS_COLS
        return pygame.Rect(self.slots_x + col * (SLOT_SIZE + SLOT_PAD), self.slots_y + fila * (SLOT_SIZE + SLOT_PAD), SLOT_SIZE, SLOT_SIZE)

    def _slot_en_pos(self, pos):
        for i in range(SLOTS_TOTAL):
            if self._slot_rect(i).collidepoint(pos): return i
        return -1

    def _boton_accion_rect(self):
        return pygame.Rect(self.panel_x + self.panel_w - 280, self.panel_y + self.panel_h - 70, 240, 40)

    def _boton_cerrar_rect(self):
        return pygame.Rect(self.panel_x + self.panel_w - 40, self.panel_y + 12, 28, 28)

    def mouse_encima(self, pos):
        if self.boton.collidepoint(pos): return True
        return self.abierto and self.panel_rect.collidepoint(pos)

    def click(self, pos, inventario, jugador):
        if self.boton.collidepoint(pos):
            self.abierto = not self.abierto
            if not self.abierto:
                self.arrastrando = False
                self.arrastre_desde = -1
                self.slot_seleccionado = -1
            return
        if not self.abierto: return
        if self._boton_cerrar_rect().collidepoint(pos):
            self.abierto = False
            return
        if self._boton_accion_rect().collidepoint(pos):
            if self.slot_seleccionado != -1:
                item = inventario.slots[self.slot_seleccionado]
                if item:
                    item_id = item["id"]
                    if es_consumible(item_id): inventario.usar(self.slot_seleccionado, jugador)
                    else:
                        if item_id == "espada_infernal" and not jugador.espada_equipada: jugador.equipar_item(item_id)
                        elif item_id == "armadura_infernal":
                            if jugador.armadura_equipada: jugador.desequipar_item(item_id)
                            else: jugador.equipar_item(item_id)
            return
        idx = self._slot_en_pos(pos)
        if idx != -1:
            self.slot_seleccionado = idx
            if inventario.slots[idx] is not None:
                self.arrastrando = True
                self.arrastre_desde = idx
                sr = self._slot_rect(idx)
                self.mouse_offset = (pos[0] - sr.x, pos[1] - sr.y)

    def soltar(self, pos, inventario):
        if not self.abierto or not self.arrastrando: return
        idx = self._slot_en_pos(pos)
        if idx != -1 and idx != self.arrastre_desde: inventario.mover(self.arrastre_desde, idx)
        self.arrastrando = False
        self.arrastre_desde = -1

    def _dibujar_icono(self, pantalla, item_id, rect):
        info = ITEMS.get(item_id)
        if not info: return
        cx, cy = rect.center
        color, borde, forma, tam = info["color"], info["color_borde"], info["forma"], int(rect.w * 0.55)

        if forma == "rect":
            r = pygame.Rect(0, 0, tam, tam); r.center = (cx, cy)
            pygame.draw.rect(pantalla, color, r); pygame.draw.rect(pantalla, borde, r, 2)
        elif forma == "rombo":
            pts = [(cx, cy - tam // 2), (cx + tam // 2, cy), (cx, cy + tam // 2), (cx - tam // 2, cy)]
            pygame.draw.polygon(pantalla, color, pts); pygame.draw.polygon(pantalla, borde, pts, 2)
        elif forma == "corazon":
            pygame.draw.circle(pantalla, color, (cx - tam // 4, cy - 2), tam // 3)
            pygame.draw.circle(pantalla, color, (cx + tam // 4, cy - 2), tam // 3)
            pts = [(cx - tam // 2 + 4, cy + 2), (cx + tam // 2 - 4, cy + 2), (cx, cy + tam // 2)]
            pygame.draw.polygon(pantalla, color, pts); pygame.draw.polygon(pantalla, borde, pts, 2)
        elif forma == "armadura":
            pts = [(cx - tam // 2, cy - tam // 2), (cx + tam // 2, cy - tam // 2), (cx + tam // 3, cy + tam // 2), (cx - tam // 3, cy + tam // 2)]
            pygame.draw.polygon(pantalla, color, pts); pygame.draw.polygon(pantalla, borde, pts, 2)
        elif forma == "espada":
            pygame.draw.polygon(pantalla, (220, 220, 230), [(cx, cy - tam // 2), (cx + tam // 8, cy - tam // 4), (cx + tam // 8, cy + tam // 4), (cx, cy + tam // 3), (cx - tam // 8, cy + tam // 4), (cx - tam // 8, cy - tam // 4)])
            pygame.draw.polygon(pantalla, (255, 100, 0), [(cx - tam // 8, cy - tam // 4), (cx - tam // 2, cy), (cx - tam // 8, cy + tam // 4)])
            pygame.draw.polygon(pantalla, (255, 200, 0), [(cx + tam // 8, cy - tam // 4), (cx + tam // 2, cy), (cx + tam // 8, cy + tam // 4)])
            pygame.draw.rect(pantalla, borde, (cx - tam // 3, cy + tam // 3, tam * 2 // 3, tam // 8))
            pygame.draw.rect(pantalla, (100, 60, 30), (cx - tam // 12, cy + tam // 3 + tam // 8, tam // 6, tam // 4))

    def dibujar(self, pantalla, inventario, jugador, mouse_pos):
        pygame.draw.rect(pantalla, (240, 240, 240), self.boton, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.boton, 2, border_radius=6)
        f_boton = pygame.font.SysFont(None, 24)
        pantalla.blit(f_boton.render("Inventario", True, COLOR_BORDE), (self.boton.x + 10, self.boton.y + 8))

        if not self.abierto: return

        overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150))
        pantalla.blit(overlay, (0, 0))
        pygame.draw.rect(pantalla, COLOR_PANEL, self.panel_rect, border_radius=12)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.panel_rect, 4, border_radius=12)
        pantalla.blit(fuente_titulo.render("Inventario", True, COLOR_BORDE), (self.panel_x + 20, self.panel_y + 16))

        cerrar_r = self._boton_cerrar_rect()
        pygame.draw.rect(pantalla, (200, 80, 80), cerrar_r, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_BORDE, cerrar_r, 2, border_radius=6)
        pantalla.blit(fuente_info.render("X", True, (255, 255, 255)), (cerrar_r.centerx - 6, cerrar_r.centery - 8))

        self.slot_hover = self._slot_en_pos(mouse_pos)
        for i in range(SLOTS_TOTAL):
            sr = self._slot_rect(i)
            color = COLOR_SLOT_SEL if i == self.slot_seleccionado else (COLOR_SLOT_HOVER if i == self.slot_hover else COLOR_SLOT)
            pygame.draw.rect(pantalla, color, sr, border_radius=6)
            pygame.draw.rect(pantalla, COLOR_SLOT_BORDE, sr, 2, border_radius=6)

            item = inventario.slots[i]
            if item and not (self.arrastrando and i == self.arrastre_desde):
                self._dibujar_icono(pantalla, item["id"], sr)
                if item["cantidad"] > 1:
                    txt = fuente_slot.render(str(item["cantidad"]), True, (255, 255, 255))
                    sombra = fuente_slot.render(str(item["cantidad"]), True, (0, 0, 0))
                    pantalla.blit(sombra, (sr.right - txt.get_width() - 5, sr.bottom - txt.get_height() - 3))
                    pantalla.blit(txt, (sr.right - txt.get_width() - 6, sr.bottom - txt.get_height() - 4))

        info_x = self.slots_x + SLOTS_COLS * (SLOT_SIZE + SLOT_PAD) + 15
        info_y = self.slots_y
        if self.slot_seleccionado != -1:
            item = inventario.slots[self.slot_seleccionado]
            if item: self._dibujar_info(pantalla, item, info_x, info_y, jugador)
        else:
            pantalla.blit(fuente_chica.render("Click en un item para ver info.", True, (120, 100, 80)), (info_x, info_y))

        if self.arrastrando and self.arrastre_desde != -1:
            item = inventario.slots[self.arrastre_desde]
            if item:
                drag_rect = pygame.Rect(0, 0, SLOT_SIZE, SLOT_SIZE)
                drag_rect.topleft = (mouse_pos[0] - self.mouse_offset[0], mouse_pos[1] - self.mouse_offset[1])
                drag_surf = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(drag_surf, (*COLOR_SLOT_SEL, 180), drag_surf.get_rect(), border_radius=6)
                self._dibujar_icono(drag_surf, item["id"], drag_surf.get_rect())
                if item["cantidad"] > 1:
                    txt = fuente_slot.render(str(item["cantidad"]), True, (255, 255, 255))
                    drag_surf.blit(txt, (SLOT_SIZE - txt.get_width() - 4, SLOT_SIZE - txt.get_height() - 3))
                pantalla.blit(drag_surf, drag_rect.topleft)

    def _dibujar_info(self, pantalla, item, x, y, jugador):
        info = ITEMS.get(item["id"])
        if not info: return
        pantalla.blit(fuente_info.render(info["nombre"], True, COLOR_BORDE), (x, y))
        y += 30

        icono_rect = pygame.Rect(x, y, 80, 80)
        pygame.draw.rect(pantalla, COLOR_SLOT, icono_rect, border_radius=8)
        pygame.draw.rect(pantalla, COLOR_SLOT_BORDE, icono_rect, 2, border_radius=8)
        self._dibujar_icono(pantalla, item["id"], icono_rect)
        y += 95
        pantalla.blit(fuente_chica.render(f"Cantidad: {item['cantidad']}", True, COLOR_TEXTO), (x, y))
        y += 24

        palabras = info["descripcion"].split()
        linea = ""
        for p in palabras:
            prueba = linea + " " + p if linea else p
            if fuente_chica.size(prueba)[0] > 260:
                pantalla.blit(fuente_chica.render(linea, True, COLOR_TEXTO), (x, y))
                y += 20; linea = p
            else: linea = prueba
        if linea: pantalla.blit(fuente_chica.render(linea, True, COLOR_TEXTO), (x, y))

        accion_rect = self._boton_accion_rect()
        mostrar_boton = True
        texto_boton = ""
        color_btn = (100, 180, 100)

        if es_consumible(item["id"]): texto_boton = "Usar"
        elif item["id"] == "espada_infernal":
            if jugador.espada_equipada: texto_boton, color_btn = "Equipada", (150, 150, 150)
            else: texto_boton = "Equipar"
        elif item["id"] == "armadura_infernal":
            if jugador.armadura_equipada: texto_boton, color_btn = "Desequipar", (200, 100, 100)
            else: texto_boton = "Equipar"
        else: mostrar_boton = False

        if mostrar_boton:
            pygame.draw.rect(pantalla, color_btn, accion_rect, border_radius=8)
            pygame.draw.rect(pantalla, COLOR_BORDE, accion_rect, 2, border_radius=8)
            txt = fuente_info.render(texto_boton, True, (255, 255, 255))
            pantalla.blit(txt, (accion_rect.centerx - txt.get_width() // 2, accion_rect.centery - txt.get_height() // 2))