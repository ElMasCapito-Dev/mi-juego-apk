import pygame
import math

class ControlesTactiles:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.mostrar = False
        
        self.izq = False
        self.der = False
        self.saltar = False
        
        self.atacar_click = False
        self.z_click = False
        self.transformar_press = False
        self.interactuar_press = False # <--- NUEVO

        self.btn_izq = pygame.Rect(40, alto - 110, 70, 70)
        self.btn_der = pygame.Rect(130, alto - 110, 70, 70)

        self.btn_salto = pygame.Rect(ancho - 100, alto - 200, 70, 70)
        self.btn_atacar = pygame.Rect(ancho - 100, alto - 100, 80, 80)
        self.btn_z = pygame.Rect(ancho - 180, alto - 120, 60, 60)
        self.btn_trans = pygame.Rect(ancho - 180, alto - 210, 60, 60)
        
        # Botón de interactuar (al lado del saltar)
        self.btn_interactuar = pygame.Rect(ancho - 260, alto - 200, 70, 70)

    def procesar_evento(self, evento):
        if not self.mostrar: return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_izq.collidepoint(evento.pos): self.izq = True
            if self.btn_der.collidepoint(evento.pos): self.der = True
            if self.btn_salto.collidepoint(evento.pos): self.saltar = True
            
            if self.btn_atacar.collidepoint(evento.pos): self.atacar_click = True
            if self.btn_z.collidepoint(evento.pos): self.z_click = True
            if self.btn_trans.collidepoint(evento.pos): self.transformar_press = True
            if self.btn_interactuar.collidepoint(evento.pos): self.interactuar_press = True

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.izq = False
            self.der = False
            self.saltar = False
            self.atacar_click = False
            self.z_click = False
            self.transformar_press = False
            self.interactuar_press = False

    def dibujar(self, pantalla, tiene_espada, puede_transformar):
        if not self.mostrar: return

        def dibujar_btn(rect, texto, color=(100, 100, 100, 150), borde=15):
            surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, surf.get_rect(), border_radius=borde)
            pantalla.blit(surf, rect.topleft)
            
            f = pygame.font.SysFont(None, 30 if len(texto) < 5 else 22)
            txt = f.render(texto, True, (255, 255, 255))
            pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        dibujar_btn(self.btn_izq, "<")
        dibujar_btn(self.btn_der, ">")
        dibujar_btn(self.btn_salto, "SALTO", (50, 150, 50, 180), 35)
        dibujar_btn(self.btn_atacar, "ATACAR", (200, 100, 50, 180), 40)
        
        # Botón de interactuar en amarillo
        dibujar_btn(self.btn_interactuar, "E", (200, 200, 50, 180), 35)

        if tiene_espada:
            dibujar_btn(self.btn_z, "Z", (200, 50, 50, 180), 30)
            
        if puede_transformar:
            dibujar_btn(self.btn_trans, "T", (150, 50, 200, 180), 30)

    def obtener_teclas_falsas(self):
        return {pygame.K_a: self.izq, pygame.K_d: self.der}